from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# run only once
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()


def classify_tweet(text):
    score = sia.polarity_scores(text)['compound']

    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"
