"""Django command to check the authentification on Github API as an app."""
import json

from django.core.management.base import BaseCommand

from dashboard_apps.utils import GithubAPI


class Command(BaseCommand):
    """Command definition."""

    help = 'test github auth as an app'

    def handle(self, *args, **options):
        """Command entrypoint."""
        self.stdout.write(json.dumps(GithubAPI().get('/app')))
