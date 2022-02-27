from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os


class Command(BaseCommand):
    """Custom command for when initiating python "manage.py".
    Populates the database which has been defined in the settings module of the base app.
    """

    help = 'Populates the database with collections and products'

    def handle(self, *args, **options):
        print('Populating the database...')
        current_dir = os.path.dirname(__file__)  # Getting current directory.
        file_path = os.path.join(current_dir, 'seed.sql')  # Joining with this.
        # Using "Path" class, the entire text is read to the file, which will return the SQL instructions.
        sql = Path(file_path).read_text()

        with connection.cursor() as cursor:  # Opening a connection to the DB.
            cursor.execute(sql)  # Executing the SQL statement.
