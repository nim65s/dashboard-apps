"""Various utilities for dashboard-apps."""
from time import time
from typing import Any, Dict

import jwt
import requests
from django.conf import settings


class Singleton(type):
    """Metaclass to create singletons."""

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        """On class instanciation, return the existing one if any."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GithubAPI(metaclass=Singleton):
    """Helpers for https://api.github.com.

    example use:
    github_api = GithubAPI()
    github_api.get('/app')
    """

    TOKEN_VALIDITY = 10 * 60  # seconds
    TOKEN_RESET = 8 * 60

    def __init__(self):
        """Define class members."""
        self._token_time = 0
        self._token = ''

    def _update_token(self):
        self._token_time = int(time())

        self._token = jwt.encode(
            {
                'iat': self._token_time,
                'exp': self._token_time + self.TOKEN_VALIDITY,
                'iss': settings.GITHUB_APP_ID
            },
            settings.GITHUB_PRIVATE_KEY,
            algorithm="RS256").decode()

    @property
    def token(self):
        """Get a jwt."""
        if time() > self._token_time + self.TOKEN_RESET:
            self._update_token()
        return self._token

    @property
    def _headers(self):
        return {'Authorization': f'Bearer {self.token}', 'Accept': 'application/vnd.github.machine-man-preview+json'}

    def get(self, path, params=None):
        """Perform an HTTP GET on the API."""
        return requests.get('https://api.github.com' + path, params=params, headers=self._headers).json()

    def post(self, path, data=None, json=None):
        """Perform an HTTP POST on the API."""
        return requests.post('https://api.github.com' + path, data=data, json=json, headers=self._headers).json()
