import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# TODO: Store the id of the most recent responded tweet, which is then used when responding to newer mentions
last_responded_tweet_id = 0


def reply_tweets():
    mentions = api.mentions_timeline(count=30, since_id=last_responded_tweet_id)
    for mention in reversed(mentions):
        print("Hello world!")  # TODO: implement the reply functionality
