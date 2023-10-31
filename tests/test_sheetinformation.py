from datetime import datetime
import pytest
from lib.classes import SheetInformation

class TestSheetInformation:
    
    
    def test_email_is_valid__true(self):
        t = SheetInformation(email='test@valid.com')
        assert t.email_is_valid(), "E-mail test@valid.com reported as invalid"

    def test_email_is_valid__false(self):
        t = SheetInformation(email='testinvalid.com')
        assert t.email_is_valid() is False, "E-mail testinvalid.com reported as valid" 

    def test_get__no_attr(self):
        t = SheetInformation()
        with pytest.raises(AttributeError):
            t.get('no_attr'), "This should have thrown an AttributeError as the attribute does not exist"
        
    def test_get__game(self):
        t = SheetInformation()

        assert t.get('game') == ''

    def test_set__no_attr(self):
        t = SheetInformation()

        with pytest.raises(AttributeError):
            t.set('no_attr', None), "This should have thrown an AttributeError as the attribute does not exist"

    def test_set__game(self):
        t = SheetInformation()

        t.set('game', 'foo')

        assert t.game == 'foo'

    def test_is_proper_sanctioned_date__default(self):
        t = SheetInformation()

        assert t.sanctioned_date_is_valid(), "This should return True by default as the given_sanctioned_date is not set"

    def test_is_proper_sanctioned_date__false(self):
        t = SheetInformation()
        t.given_sanctioned_date = '23/13/01'

        assert t.sanctioned_date_is_valid() == False, "Date string '23/13/01' should not be valid"


    def test_is_proper_sanctioned_date__formats(self):
        t = SheetInformation()
        # '%m/%d/%y'
        t.given_sanctioned_date = '1/13/23'
        assert t.sanctioned_date_is_valid(), "Format: 1/13/23 should be valid"

        t.given_sanctioned_date = '01/13/23'
        assert t.sanctioned_date_is_valid(), "Format: 01/13/23 should be valid"

        # '%m/%d/%Y'
        t.given_sanctioned_date = '01/13/2023'
        assert t.sanctioned_date_is_valid(), "Format: 01/13/2023 should be valid"

        t.given_sanctioned_date = '1/13/2023'
        assert t.sanctioned_date_is_valid(), "Format: 1/13/2023 should be valid"
        
        # '%Y-%m-%d'
        t.given_sanctioned_date = '2023-01-13'
        assert t.sanctioned_date_is_valid(), "Format: 2023-01-13 should be valid"

    
    def test_get_formatted_sanction_date(self) -> str:
        format = '%Y-%m-%d'
        date = datetime.strptime('2023-01-13', format)
        t = SheetInformation(sanction_date=date)

        # Default format
        assert t.get_formatted_sanction_date() == '01/13/2023'

        # Given a format
        assert t.get_formatted_sanction_date(format=format) == '2023-01-13'

    def test_valid_storyteller__true(self):
        t = SheetInformation(storyteller='TestRunner')

        assert t.storyteller_is_valid()

    def test_valid_storyteller__false(self):
        t = SheetInformation()

        assert not t.storyteller_is_valid()


    def test_callings_defined__true(self):
        t = SheetInformation(game='scion', callings=['calling1', 'calling2', 'calling3'])

        assert t.callings_defined()

    def test_callings_defined__false(self):
        t = SheetInformation(game='scion')

        assert not t.callings_defined(), "Callings should be None"

        t.callings = ['calling1', 'calling2']
        assert not t.callings_defined(), "Too few callings"

    
    def test_callings_defined__irrelevant(self):
        t = SheetInformation() # Game isn't Scion, so Callings is unneeded
        assert t.callings_defined()


    def test_get_wrapped_callings(self):
        t = SheetInformation(callings=['calling1', 'calling2', 'calling3'])

        assert t.get_wrapped_callings() == [['calling1'], ['calling2'], ['calling3']]







