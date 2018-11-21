from unittest import TestCase, mock
from title_api.main import app
from title_api.extensions import db
from title_api.models import Conveyancer

conveyancer = Conveyancer("O=Conveyancer1,L=Plymouth,C=GB", "ConveyIt")

conveyancer_x500_dict = {
    "organisation": "Conveyancer1",
    "organisational_unit": None,
    "country": "GB",
    "locality": "Plymouth",
    "state": None,
    "common_name": None
}


class TestConveyancer(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_happy_path_get_conveyancers(self, mock_db_query):
        """Gets a list of all conveyancers."""
        mock_db_query.all.return_value = [conveyancer]
        resp = self.app.get('/v1/conveyancers', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 1)

    @mock.patch.object(db.Model, 'query')
    def test_002_happy_path_get_conveyancer_by_conveyancer_id(self, mock_db_query):
        """Gets the conveyancer with the specified conveyancer ID."""
        mock_db_query.get.return_value = conveyancer
        resp = self.app.get('/v1/conveyancers/1', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['x500'], conveyancer_x500_dict)
        self.assertEqual(resp.json['company_name'], "ConveyIt")
