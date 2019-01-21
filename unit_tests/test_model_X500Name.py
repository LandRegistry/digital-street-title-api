from unittest import TestCase
from title_api.main import app
from title_api.models import X500Name
import copy

# Test data
standard_string1 = "CN=Generic Conveyancing Company, OU=Digital, O=Generic Conveyancing Company, \
                    L=Plymouth, ST=Devon, C=GB"
standard_string2 = "O=Generic Conveyancing Company,L=Plymouth,C=GB,ST=Devon,OU=Digital,CN=Generic Conveyancing Company"
standard_string3 = "O=Generic Conveyancing Company, L=Plymouth, ST=Devon, C=GB"
standard_string4 = "O=Generic Conveyancing Company, L=Plymouth, C=GB"
standard_string5 = "O=Generic Conveyancing Company, L=Plymouth, ST=Devon"
standard_string6 = "O=C, L=P, C=USA"
standard_dict1 = {
    'common_name': 'Generic Conveyancing Company',
    'organisational_unit': 'Digital',
    'organisation': 'Generic Conveyancing Company',
    'locality': 'Plymouth',
    'state': 'Devon',
    'country': 'GB'
}
standard_dict2 = {
    'organisation': 'Generic Conveyancing Company',
    'locality': 'Plymouth',
    'state': 'Devon',
    'country': 'GB'
}
standard_dict3 = {
    'organisation': 'Generic Conveyancing Company',
    'locality': 'Plymouth',
    'country': 'GB'
}
standard_dict4 = {
    'organisation': 'Generic Conveyancing Company',
    'locality': 'Plymouth',
    'state': 'Devon'
}
standard_dict5 = {
    'organisation': 'C',
    'locality': 'P',
    'country': 'USA'
}


# Tests the X500Name class
class TestModelX500Name(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    def test_001_x500name_init(self):
        """Creating a new X500Name object via the init method."""
        x500name = X500Name('Generic Conveyancing Company', 'Plymouth', 'GB')
        self.compare_against_standard(x500name, False, False, False)

        x500name.state = 'Devon'
        x500name.organisational_unit = 'Digital'
        x500name.common_name = 'Generic Conveyancing Company'
        self.compare_against_standard(x500name)

    def test_002_x500name_init_missing_val(self):
        """Required value not passed to the init method."""
        with self.assertRaises(TypeError) as e:
            X500Name('Generic Conveyancing Company', 'Plymouth')
        self.assertIn('missing', str(e.exception))
        self.assertIn('country', str(e.exception))

    def test_003_x500name_from_string(self):
        """Creates an X500Name from a serialised string."""
        x500name = X500Name.from_string(standard_string1)
        self.compare_against_standard(x500name, True, True, True)

        x500name = X500Name.from_string(standard_string2)
        self.compare_against_standard(x500name, True, True, True)

        x500name = X500Name.from_string(standard_string3)
        self.compare_against_standard(x500name, True, False, False)

        x500name = X500Name.from_string(standard_string4)
        self.compare_against_standard(x500name, False, False, False)

    def test_004_x500name_from_string_missing_val(self):
        """Required values missing from serialised string."""
        with self.assertRaises(TypeError) as e:
            X500Name.from_string(standard_string5)
        self.assertIn('Missing: country', str(e.exception))

    def test_005_x500name_from_string_fail_validate(self):
        """Value in serialised string does not meet the requirements."""
        with self.assertRaises(ValueError) as e:
            X500Name.from_string(standard_string6)
        self.assertIn('Wrong length: ', str(e.exception))

    def test_006_x500name_from_dict(self):
        """Creates an X500Name from a dictionary."""
        x500name = X500Name.from_dict(standard_dict1)
        self.compare_against_standard(x500name, True, True, True)

        x500name = X500Name.from_dict(standard_dict2)
        self.compare_against_standard(x500name, True, False, False)

        x500name = X500Name.from_dict(standard_dict3)
        self.compare_against_standard(x500name, False, False, False)

    def test_007_x500name_from_dict_missing_val(self):
        """Required value missing from dictionary."""
        with self.assertRaises(KeyError) as e:
            X500Name.from_dict(standard_dict4)
        self.assertIn('country', str(e.exception))

    def test_008_x500name_from_dict_fail_validate(self):
        """Value in dictionary does not meet the requirements."""
        with self.assertRaises(ValueError) as e:
            X500Name.from_dict(standard_dict5)
        self.assertIn('Wrong length: ', str(e.exception))

    def test_009_x500name_validate_missing_val(self):
        """Required values do not exist."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(TypeError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = None
            x.validate()
        self.assertIn('Missing: organisation', str(e.exception))

        with self.assertRaises(TypeError) as e:
            x = copy.deepcopy(x500name)
            x.locality = None
            x.validate()
        self.assertIn('Missing: locality', str(e.exception))

        with self.assertRaises(TypeError) as e:
            x = copy.deepcopy(x500name)
            x.country = None
            x.validate()
        self.assertIn('Missing: country', str(e.exception))

    def test_010_x500name_validate_length(self):
        """Values are not of the correct length, as per the requirements."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'A'
            x.validate()
        self.assertIn('Wrong length: organisation', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'A' * 129
            x.validate()
        self.assertIn('Wrong length: organisation', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.locality = 'A'
            x.validate()
        self.assertIn('Wrong length: locality', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.locality = 'A' * 65
            x.validate()
        self.assertIn('Wrong length: locality', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.country = 'A'
            x.validate()
        self.assertIn('Wrong length: country', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.country = 'A' * 3
            x.validate()
        self.assertIn('Wrong length: country', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.state = 'A'
            x.validate()
        self.assertIn('Wrong length: state', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.state = 'A' * 65
            x.validate()
        self.assertIn('Wrong length: state', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisational_unit = 'A'
            x.validate()
        self.assertIn('Wrong length: organisational_unit', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisational_unit = 'A' * 65
            x.validate()
        self.assertIn('Wrong length: organisational_unit', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.common_name = 'A'
            x.validate()
        self.assertIn('Wrong length: common_name', str(e.exception))

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.common_name = 'A' * 65
            x.validate()
        self.assertIn('Wrong length: common_name', str(e.exception))

    def test_011_x500name_validate_first_char_case(self):
        """The value's first character is lowercase."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'conveyIt'
            x.validate()
        self.assertIn('First character is not uppercase: organisation', str(e.exception))

    def test_012_x500name_validate_leading_trailing_whitespace(self):
        """The value has leading or trailing whitespace."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'Generic Conveyancing Company '
            x.validate()
        self.assertIn('Has leading or trailing whitespace: organisation', str(e.exception))

    def test_013_x500name_validate_invalid_chars(self):
        """The value contains invalid characters."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'It, \'Convey\' = \"-$\"'
            x.validate()
        self.assertIn('Contains invalid characters: organisation', str(e.exception))

    def test_014_x500name_validate_null_chars(self):
        """The value contains a null character."""
        x500name = X500Name.from_dict(standard_dict1)

        with self.assertRaises(ValueError) as e:
            x = copy.deepcopy(x500name)
            x.organisation = 'Generic Conveyancing Company\00'
            x.validate()
        self.assertIn('Contains null character: organisation', str(e.exception))

    def test_015_x500name_str(self):
        """Creates a serialised string of the X500Name object."""
        x500name = X500Name.from_dict(standard_dict1)
        self.assertEqual(str(x500name), standard_string2)

    def test_016_x500name_repr(self):
        """Displays the X500Name as a serialised string."""
        x500name = X500Name.from_dict(standard_dict1)
        self.assertEqual(repr(x500name), standard_string2)

    def test_017_x500name_as_dict(self):
        """Gets the X500Name as a dictionary."""
        x500name = X500Name.from_string(standard_string1)
        self.compare_dict_against_standard(x500name.as_dict())

    def compare_against_standard(self, x500name, is_s_set=True, is_ou_set=True, is_cn_set=True):
        """Checks if the X500Name contains the correct values for the test data at the top of the file."""
        self.assertEqual(x500name.organisation, 'Generic Conveyancing Company')
        self.assertEqual(x500name.locality, 'Plymouth')
        self.assertEqual(x500name.country, 'GB')
        self.assertEqual(x500name.state, 'Devon' if is_s_set else None)
        self.assertEqual(x500name.organisational_unit, 'Digital' if is_ou_set else None)
        self.assertEqual(x500name.common_name, 'Generic Conveyancing Company' if is_cn_set else None)

    def compare_dict_against_standard(self, dict, is_s_set=True, is_ou_set=True, is_cn_set=True):
        """Checks if an X500Name's dictionary contains the correct values for the test data at the top of the file."""
        self.assertEqual(dict['organisation'], 'Generic Conveyancing Company')
        self.assertEqual(dict['locality'], 'Plymouth')
        self.assertEqual(dict['country'], 'GB')
        self.assertEqual(dict['state'], 'Devon' if is_s_set else None)
        self.assertEqual(dict['organisational_unit'], 'Digital' if is_ou_set else None)
        self.assertEqual(dict['common_name'], 'Generic Conveyancing Company' if is_cn_set else None)
