"""Django command to check the authentification on Github API as an installation."""
import json

from django.core.management.base import BaseCommand

from dashboard_apps.utils import GithubAPI


class Command(BaseCommand):
    """Command definition."""

    help = 'test github auth as an installation of the app'

    def handle(self, *args, **options):
        """Command entrypoint."""
        path = '/app/installations/:installation_id/access_tokens'
        payload = {
            'repository_ids': [232098249],
            'permissions': {
                'checks': 'write',
                'contents': 'read',
            }
        }
        ret = GithubAPI().post(path, json=payload)
        self.stdout.write(json.dumps(ret))
        self.stdout.write(f'"Authorization: token {ret["token"]}"')
