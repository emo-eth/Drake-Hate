import unittest

# Local files
import utils
import drake_bot


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

    def test_twitter_search(self):
        # assign to local var so it only queries API once
        # assuming that running unit tests takes advantage
        # of the fact that it's a class...
        self.tweets = drake_bot.search()
        assert len(self.tweets) != 0

    def test_clean_search_results(self):
        cleaned = drake_bot.clean_search_results(self.tweets)
        # this isn't necessarily true but in practice it
        # almost certainly will be
        assert len(cleaned) < len(self.tweets) and len(cleaned) != 0

    def test_savepoint(self):
        savepoint = drake_bot.parse_savepoint_from_tweets(self.tweets)
        assert savepoint  # is not an empty string
