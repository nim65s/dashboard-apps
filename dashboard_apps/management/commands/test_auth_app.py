from time import time

from django.conf import settings
from django.core.management.base import BaseCommand

import requests

import jwt


class Command(BaseCommand):
    help = 'test github auth as an app'

    def handle(self, *args, **options):
        payload = {'iat': int(time()), 'exp': int(time()) + 600, 'iss': settings.GITHUB_APP_ID}
        token = jwt.encode(payload, settings.GITHUB_PRIVATE_KEY, algorithm="RS256").decode()
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github.machine-man-preview+json'}
        ret = requests.get('https://api.github.com/app', headers=headers).json()
        self.stdout.write(str(ret))
