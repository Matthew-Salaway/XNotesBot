import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
TWITTER_ID = os.getenv('TWITTER_ID')

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# TODO: Store the id of the most recent responded tweet, which is then used when responding to newer mentions
last_responded_tweet_id = 0


def reply_tweets():
    """
        Reply to mentions on Twitter.
        Retrieves mentions directed at the bot, generates a simple reply for each mention,
        and posts the reply back to Twitter as a reply to the original mention.
        Returns:
            int: The ID of the most recent responded tweet, which is then used when responding to newer mentions.
        """
    global last_responded_tweet_id

    mentions = client.get_users_mentions(id=TWITTER_ID)
    last_responded_tweet_id = mentions.meta.get("newest_id", "")  # handle case of missing/empty data

    for mention in reversed(mentions.data):
        # Extract the ID of the mention
        mention_id = mention.id
        # Generate your reply based on the mention
        reply_text = "Hi there, thanks for the mention!"
        # Reply to the mention
        client.create_tweet(in_reply_to_tweet_id=mention_id, text=reply_text)

    return last_responded_tweet_id


if __name__ == "__main__":
    reply_tweets()
