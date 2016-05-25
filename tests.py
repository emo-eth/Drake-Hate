import unittest

# Local files
import utils

class QuotedTextTest(unittest.TestCase):

    def test_no_quotes(self):
        str_1 = 'i hate drake'
        result = utils.remove_quoted_text(str_1)
        assert result == str_1

    def test_quoted_text(self):
        str_1 = 'i love drake "i hate drake"'
        str_2 = 'i love drake '
        result = utils.remove_quoted_text(str_1)
        assert result == str_2

    def text_mismatched_quotes(self):
        ''' If there are mismatched quotes in the input string, the 
            remove_quoted_text() function shouldn't fuck with it. 
            In this case we expect it to return the input string. 
        '''
        str_1 = '""i hate drake"'
        result = utils.remove_quoted_text(str_1)
        assert result == str_1
