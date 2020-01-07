from time import time

from django.conf import settings
from django.core.management.base import BaseCommand

import requests

import jwt


class Command(BaseCommand):
    help = 'test github auth as an installation of the app'

    def handle(self, *args, **options):
        payload = {'iat': int(time()), 'exp': int(time()) + 600, 'iss': settings.GITHUB_APP_ID}
        token = jwt.encode(payload, settings.GITHUB_PRIVATE_KEY, algorithm="RS256").decode()
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github.machine-man-preview+json'}
        url = 'https://api.github.com/app/installations/:installation_id/access_tokens'
        ret = requests.post(url, headers=headers).json()
        self.stdout.write(str(ret))
        self.stdout.write(f'"Authorization: token {ret["token"]}"')
