"""Django command to check the authentification on Github API as an installation."""
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard_apps.utils import GithubAPI


class Command(BaseCommand):
    """Command definition."""

    help = 'test github auth as an installation of the app'

    def handle(self, *args, **options):
        """Command entrypoint."""
        ret = GithubAPI().post(f'/app/installations/{settings.INSTALLATION_ID}/access_tokens')
        self.stdout.write(json.dumps(ret))
        self.stdout.write(f'"Authorization: token {ret["token"]}"')
