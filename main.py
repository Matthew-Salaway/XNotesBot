from flask import Flask
import tweepy
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

TWITTER_ID = os.getenv('TWITTER_ID')


def load_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    bearer_token = os.getenv("BEARER_TOKEN")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    return client, api


client, api = load_client()

# File path to store mentioned tweet IDs
MENTIONED_TWEETS_FILE = "mentioned_tweets.txt"


# Function to load mentioned tweet IDs from file
def load_mentioned_tweets():
    try:
        with open(MENTIONED_TWEETS_FILE, "r") as file:
            return list(int(line.strip()) for line in file)
    except FileNotFoundError:
        return list()


# Function to save mentioned tweet IDs to file
def save_mentioned_tweets(mentioned_tweets):
    with open(MENTIONED_TWEETS_FILE, "w") as file:
        for tweet_id in mentioned_tweets:
            file.write(str(tweet_id) + "\n")


# Load mentioned tweets from file
mentioned_tweets = load_mentioned_tweets()
# TODO: Store the id of the most recent responded tweet, which is then used when retrieving newer mentions
last_responded_tweet_id = mentioned_tweets[-1] if len(mentioned_tweets) > 0 else 0


@app.route("/")
def hello_world():
    return "X-Notes Twitter Bot"


@app.route("/tweets")
def fetch_tweets():
    mentions = client.get_users_mentions(id=TWITTER_ID, since_id=last_responded_tweet_id)

    last_fetched_tweet_id = mentions.meta.get("newest_id", 0)  # handle case of missing/empty data
    if not mentions.data:
        return "No new mention"

    for mention in reversed(mentions.data):
        # Extract the ID of the mention
        mention_id = mention.id
        mentioned_tweets_set = set(mentioned_tweets)
        if mention_id in mentioned_tweets_set:
            continue  # Skip if the mention has already been replied to
        mentioned_tweets.append(mention_id)
        # Generate your reply based on the mention
        reply_text = "Hi there, thanks for the mention!"
        # Reply to the mention
        client.create_tweet(in_reply_to_tweet_id=mention_id, text=reply_text)
    save_mentioned_tweets(mentioned_tweets)

    return f"last mentions id is {last_fetched_tweet_id}"
