# Thanks to custom management commands we can write our own unique
# commands that will affect all modules,models in our app(currently "mainapp")

import time
from django.db import connections  # To test wether our db is available or not
from django.db.utils import OperationalError
# OperationalError will raise an error if a db isn't available
from django.core.management.base import BaseCommand
# BaseCommand class in order to create our own custom management command


class Command(BaseCommand):
    """Django command to pause execution until the db is available"""
    def handle(self, *args, **options):
        self.stdout.write('Waiting for a database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available!'))
