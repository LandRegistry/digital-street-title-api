from unittest import TestCase, mock
from title_api.main import app
from title_api.extensions import db
from title_api.models import Owner, Address

owner_address = Address("1", "Digital Street", "Bristol", "Avon", "England", "BS2 8EN")
owner = Owner(1, "Lisa", "White", "lisa.seller@example.com", "07123456780", 'individual', owner_address)


class TestOwner(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_happy_path_get_owner_by_email_address(self, mock_db_query):
        """Gets an owner by their email address."""
        mock_db_query.filter_by.return_value.first.return_value = owner
        resp = self.app.get('/v1/owners', headers={'accept': 'application/json'},
                            query_string={'email_address': "lisa.seller@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['phone_number'], "07123456780")

    @mock.patch.object(db.Model, 'query')
    def test_002_unhappy_path_get_owner_no_email_address_parameter(self, mock_db_query):
        """Tries to get an owner without passing an email address."""
        resp = self.app.get('/v1/owners', headers={'accept': 'application/json'})
        assert not mock_db_query.called
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['error_message'], "'email_address' is required.")

    @mock.patch.object(db.Model, 'query')
    def test_003_happy_path_get_owner_not_found(self, mock_db_query):
        """Fails to find an owner."""
        mock_db_query.filter_by.return_value.first.return_value = None
        resp = self.app.get('/v1/owners', headers={'accept': 'application/json'},
                            query_string={'email_address': "wrong.email@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [])
