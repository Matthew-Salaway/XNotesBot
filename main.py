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
    """
        Reply to mentions on Twitter.
        Retrieves mentions directed at the bot, generates a simple reply for each mention,
        and posts the reply back to Twitter as a reply to the original mention.
        Returns:
            int: The ID of the most recent responded tweet, which is then used when responding to newer mentions.
        """
    global last_responded_tweet_id

    mentions = api.mentions_timeline(count=30, since_id=last_responded_tweet_id)

    for mention in reversed(mentions):
        # Extract the ID of the mention
        mention_id = mention.id
        # Generate your reply based on the mention
        reply_text ="Thanks for the mention!"
        # Reply to the mention
        api.update_status(status=reply_text, in_reply_to_status_id=mention_id)

        # Update the last responded tweet ID
        last_responded_tweet_id = mention_id

    return last_responded_tweet_id

if __name__=="__main__":
    reply_tweets()

