import csv
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle
import os.path

# TODO: analyze sentiment intensity with VADER
# TODO: as above, pick most negative to retweet (model is imperfect)
# TODO: learn/use maximum entropy classifier


# adapted from http://www.nltk.org/howto/sentiment.html

# dict of sentiment scores for lookup
sentiment_dict = {'4': 'positive', '2': 'neutral', '0': 'negative'}

# dict of sentiments for ease of adding docs when reading csv
dict_of_tweets = {}
for key in sentiment_dict:
    dict_of_tweets[sentiment_dict[key]] = []

SENTIMENT_COL = 0
TWEET_COL = -1

if os.path.exists('sentim_analyzer.pk1'):
    with open('sentim_analyzer.pk1', 'rb') as f:
        sentim_analyzer = pickle.load(f)

# TODO: strip of @mentions
rows = []
with open('st140u.csv', 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        sentiment = sentiment_dict[row[SENTIMENT_COL]]
        tweet = row[TWEET_COL]
        dict_of_tweets[sentiment].append((tweet, sentiment))

print("Loaded csv")


# tokenize tweets into words (& punctuation?) for feature analysis
# do this on a subset of the tweets because there are 1.6 million
# for some reason there are *no* neutral tweets in sentiment140 dataset

# neutral_docs = dict_of_tweets['neutral']
positive_tweets = [(word_tokenize(tup[0]), tup[1])
                   for tup in dict_of_tweets['positive'][:10000]]
negative_tweets = [(word_tokenize(tup[0]), tup[1])
                   for tup in dict_of_tweets['negative'][:10000]]

print(len(positive_tweets), len(negative_tweets))

# in practice, these *should* be the same
eighty_per_cent_pos = int(.8 * len(positive_tweets))
eighty_per_cent_neg = int(.8 * len(negative_tweets))

# split into training and test sets
train_pos = positive_tweets[:eighty_per_cent_pos]
test_pos = positive_tweets[eighty_per_cent_pos:]
train_neg = negative_tweets[:eighty_per_cent_neg]
test_neg = negative_tweets[eighty_per_cent_neg:]

# combine the sets
train_tweets = train_pos + train_neg
test_tweets = test_pos + test_neg

# initiate Sentiment Analyzer
# use simple unigram word features, handling negation
sentim_analyzer = SentimentAnalyzer()
all_words_neg = sentim_analyzer.all_words(
    [mark_negation(tweet) for tweet in train_tweets])
unigram_feats = sentim_analyzer.unigram_word_feats(all_words_neg, min_freq=4)
print(unigram_feats)
sentim_analyzer.add_feat_extractor(
    extract_unigram_feats, unigrams=unigram_feats)

# apply features to obtain a feature-value representation of our datasets
training_set = sentim_analyzer.apply_features(train_tweets)
test_set = sentim_analyzer.apply_features(test_tweets)

#trainer = NaiveBayesClassifier.train
#maximum entropy classifier does 100 iterations ;_;
trainer = MaxentClassifier.train
classifier = sentim_analyzer.train(trainer, training_set)
for key, value in sorted(sentim_analyzer.evaluate(test_set).items()):
    print('{0}: {1}'.format(key, value))
    # TODO: analyze intensity with VADER

with open('sentim_analyzer.pk1', 'wb') as f:
    pickle.dump(sentim_analyzer, f)

with open('trainer.pk1', 'wb') as f:
    pickle.dump(trainer, f)

with open('classifier.pk1', 'wb') as f:
    pickle.dump(classfier, f)
