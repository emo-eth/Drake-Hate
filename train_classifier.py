"""Scripts used to train the Naive Bayes and Maximum Entropy Classifiers.

Adapted from http://www.nltk.org/howto/sentiment.html
"""
import csv
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.sentiment import SentimentAnalyzer
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from nltk.sentiment.util import *
import pickle

# Index of columns in our CSV file.
TWEET_COL = 0
SENTIMENT_COL = 1

# Legend of sentiment values in our CSV data file.
SENTIMENT_DICT = {'1': 'negative', '0': 'positive'}

MIN_WORD_FREQUENCY = 2
MAX_ENTROPY_ITERATIONS = 100


def load_data_from_csv():
    # Initialize a dictionary with two keys, "negative" and "positive", which
    # will hold lists of classified tweets.
    dict_of_tweets = {}
    dict_of_tweets['negative'] = []
    dict_of_tweets['positive'] = []

    # Load our CSV data into the dictionary.
    with open('data/drake_tweets.csv', 'r', encoding='macroman') as f:
        reader = csv.reader(f)
        for row in reader:
            sentiment = SENTIMENT_DICT[row[SENTIMENT_COL]]
            tweet = row[TWEET_COL]
            dict_of_tweets[sentiment].append((tweet, sentiment))

    print("Loaded CSV file...")
    return dict_of_tweets


def initialize_sentiment_analyzer(train_tweets):
    # Initiate a sentiment analyzer.
    analyzer = SentimentAnalyzer()

    # Append '_NEG' to words following a negation word.
    all_words_neg = analyzer.all_words(
        [mark_negation(tweet) for tweet in train_tweets])

    # Get a list of all of the unigram features (words), including the list of
    # words with '_NEG' appended to them, that occur at least
    # MIN_WORD_FREQUENCY times in our dataset.
    unigram_feats = analyzer.unigram_word_feats(
        all_words_neg, min_freq=MIN_WORD_FREQUENCY)

    analyzer.add_feat_extractor(
        extract_unigram_feats, unigrams=unigram_feats)

    return analyzer


def print_results(analyzer, test_set):
    for key, value in sorted(analyzer.evaluate(test_set).items()):
        print('{0}: {1}'.format(key, value))


def train_naive_bayes(train_tweets, test_tweets):
    analyzer = initialize_sentiment_analyzer(train_tweets)

    # Apply our unigram features to the training and test datasets to get a
    # feature-value representation of our dataset.
    training_set = analyzer.apply_features(train_tweets)
    test_set = analyzer.apply_features(test_tweets)

    # Train the Naive Bayes Classifier.
    naive_bayes = analyzer.train(
        NaiveBayesClassifier.train, training_set)

    print_results(analyzer, test_set)

    with open('naive_bayes/analyzer.pk1', 'wb') as f:
        pickle.dump(analyzer, f)
    with open('naive_bayes/classifier.pk1', 'wb') as f:
        pickle.dump(naive_bayes, f)

    return naive_bayes


def train_max_ent(train_tweets, test_tweets):
    analyzer = initialize_sentiment_analyzer(train_tweets)

    # Apply our unigram features to the training and test datasets to get a
    # feature-value representation of our dataset.
    training_set = analyzer.apply_features(train_tweets)
    test_set = analyzer.apply_features(test_tweets)

    # NOTE: The Maximum Entropy Classifier is really slow!
    max_ent = analyzer.train(MaxentClassifier.train, training_set,
                             algorithm='GIS', max_iter=MAX_ENTROPY_ITERATIONS)

    print_results(analyzer, test_set)

    with open('max_ent/analyzer.pk1', 'wb') as f:
        pickle.dump(analyzer, f)
    with open('max_ent/classifier.pk1', 'wb') as f:
        pickle.dump(max_ent, f)

    return max_ent


dict_of_tweets = load_data_from_csv()

positive_tweets = [(word_tokenize(tup[0]), tup[1])
                   for tup in dict_of_tweets['positive']]
negative_tweets = [(word_tokenize(tup[0]), tup[1])
                   for tup in dict_of_tweets['negative']]

num_negative_tweets = len(negative_tweets)

print("Found {0} positive tweets and {1} negative tweets...".format(
    len(positive_tweets), num_negative_tweets))

# Split into training and test sets.
num_train_tweets = int(num_negative_tweets * 0.8)
train_pos = positive_tweets[:num_train_tweets]
train_neg = negative_tweets[:num_train_tweets]

test_pos = positive_tweets[num_train_tweets:num_negative_tweets]
test_neg = negative_tweets[num_train_tweets:]

# Combine the two sets.
train_tweets = train_pos + train_neg
test_tweets = test_pos + test_neg

# Train our classifiers.
train_naive_bayes(train_tweets, test_tweets)
# train_max_ent(train_tweets, test_tweets)
