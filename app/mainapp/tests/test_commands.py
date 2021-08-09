from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_db_be_ready(self):
        """Test waiting a db when it gets available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gitem:
            gitem.return_value = True  # patch looks the marked object and
        # replaces it with Mock object, which in our case is git.return=True.
        # gitem.return_value=True means that we manually setting the Database
        # to available when the call was performed.
            call_command("wait_for_db")
            self.assertEqual(gitem.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gitem:
            gitem.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_db")
            self.assertEqual(gitem.call_count, 6)
