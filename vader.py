import csv
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# testing VADER fun

# adapted from http://www.nltk.org/howto/sentiment.html
sid = SentimentIntensityAnalyzer()

# dict of sentiment scores for lookup
sentiment_dict = {'4': 'positive', '2': 'neutral', '0': 'negative'}

# dict of sentiments for ease of adding docs when reading csv
dict_of_tweets = {}
for key in sentiment_dict:
    dict_of_tweets[sentiment_dict[key]] = []

SENTIMENT_COL = 0
TWEET_COL = -1


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
positive_tweets = dict_of_tweets['positive'][:100]
negative_tweets = dict_of_tweets['negative'][:100]

for sentence in positive_tweets:
    print(sentence[0])
    ss = sid.polarity_scores(sentence[0])
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print()
