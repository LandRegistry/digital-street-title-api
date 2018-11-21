from unittest import TestCase, mock
from title_api.main import app
from title_api.extensions import db
from title_api.models import Title, Owner, Address

import json

owner_address = Address("1", "Digital Street", "Bristol", "Avon", "England", "BS2 8EN")
title_address = Address("1", "Digital Street", "Bristol", "Avon", "England", "BS2 8EN")
owner = Owner(1, "Lisa", "White", "lisa.seller@example.com", "07123456780", 'individual', owner_address)

title = Title("RTV237250", owner, title_address)

owner_request = owner.as_dict()
owner_request['address'] = owner_address.as_dict()

title_request = {
    "owner": owner_request,
}


class TestTitle(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_happy_path_get_titles_by_email_address(self, mock_db_query):
        """Gets a list of titles by owner's email address."""
        mock_db_query.filter_by.return_value.first.return_value = owner
        mock_db_query.filter_by.return_value.all.return_value = [title]
        resp = self.app.get('/v1/titles', headers={'accept': 'application/json'},
                            query_string={'owner_email_address': "lisa.seller@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['title_number'], "RTV237250")

    def test_002_unhappy_path_get_titles_no_email_address(self):
        """Gets a list of titles - no email address given."""
        resp = self.app.get('/v1/titles', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['error_message'], "'owner_email_address' is required.")

    @mock.patch.object(db.Model, 'query')
    def test_003_happy_path_get_title_by_title_number(self, mock_db_query):
        """Gets a title with the specified title_number."""
        mock_db_query.get.return_value = title
        resp = self.app.get('/v1/titles/RTV237250', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['owner']['email_address'], "lisa.seller@example.com")
        self.assertEqual(resp.json['address']['house_name_number'], "1")

    @mock.patch.object(db.Model, 'query')
    def test_004_unhappy_path_get_title_doesnt_exist(self, mock_db_query):
        """The given title number doesn't exist."""
        mock_db_query.get.return_value = None
        resp = self.app.get('/v1/titles/RTV237250', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json['error_message'], "A title with the specified title number was not found.")

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_005_happy_path_update_title(self, mock_db_query, mock_db_add, mock_db_commit):
        """Updates the details of a title."""
        mock_db_query.get.return_value = title
        resp = self.app.put('/v1/titles/RTV237250', data=json.dumps(title_request),
                            headers={'accept': 'application/json', 'content-type': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)
        # check that the created date has been set
        assert json.loads(resp.get_data().decode())['updated_at'] is not None
