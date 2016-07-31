import pickle
from nltk.tokenize import word_tokenize

with open('naive_bayes/sentim_analyzer.pk1', 'rb') as f:
    sentim_analyzer = pickle.load(f)

with open('naive_bayes/classifier.pk1', 'rb') as f:
    classifier = pickle.load(f)


tweet = 'Lol drake is trash 😂👎🏼'
tweet2 = 'fuck drake'


def classify(tweet):
    tokens = word_tokenize(tweet)
    feats = sentim_analyzer.apply_features(tokens)
    return classifier.classify(feats[0])
