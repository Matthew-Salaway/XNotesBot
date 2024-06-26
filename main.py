from flask import Flask
import tweepy
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
import os
import openai
import requests
import json
import time
from time import sleep


load_dotenv()
app = Flask(__name__)
scheduler = APScheduler()

TWITTER_ID = os.getenv('TWITTER_ID')
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY
bearer_token = os.environ.get("BEARER_TOKEN")



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

# Tweet ID -> Text
def tweet_id_to_text(tweet_id):
    """
    This function retrieves the text of a tweet using its ID from the Twitter API, 
    handling rate limiting and returning the tweet text.
    """
    print(f"Tweet ID: {tweet_id}")
    url = "https://api.twitter.com/2/tweets?ids={}".format(tweet_id)
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)

    while response.status_code == 429:
        sleep_time = 60
        print(f"Too many requests! Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        response = requests.request("GET", url, auth=bearer_oauth)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    try: text = json_response['data'][0]['text']
    except: text = None
    return text


def bearer_oauth(r):
    """
    This method is used for bearer token authentication with the Twitter API, 
    setting the necessary headers for the request.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


def write_note(content):
    prompt = f"I'm going to show you a Tweet and I would like you to make a note for this tweet. Notes are supposed to clarify potential misinformation present in the Tweet. A helpful Note should be accurate and important. I'd like you to create a Note based on a Tweet. Here is the Tweet: {content}."
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    model_response = response['choices'][0]['message']['content']
    print(model_response)
    return model_response


# Load mentioned tweets from file
mentioned_tweets = load_mentioned_tweets()
# TODO: Store the id of the most recent responded tweet, which is then used when retrieving newer mentions
last_responded_tweet_id = mentioned_tweets[-1] if len(mentioned_tweets) > 0 else 0


@app.route("/")
def hello_world():
    print("testings")
    return "X-Notes Twitter Bot"


@app.route("/tweets")
def fetch_tweets():
    mentions = client.get_users_mentions(id=TWITTER_ID, since_id=last_responded_tweet_id, 
                                         expansions=["referenced_tweets.id"],
                                         tweet_fields=["referenced_tweets", "text", "id"])


    last_fetched_tweet_id = mentions.meta.get("newest_id", 0)  # handle case of missing/empty data
    if not mentions.data:
        print("No new mentions")
        return "No new mention"

    for mention in reversed(mentions.data):
        # Extract the ID of the mention
        mention_id = mention.id
        mentioned_tweets_set = set(mentioned_tweets)
        if mention_id in mentioned_tweets_set:
            continue  # Skip if the mention has already been replied to
        mentioned_tweets.append(mention_id)
        # Replace line below with 
        # tweet_text = tweet_id_to_text(mention_id)
        original_tweet_id = mention.data['referenced_tweets'][0]['id']
        original_tweet_text = tweet_id_to_text(original_tweet_id)
        # Generate your reply based on the mention
        reply_text = write_note(original_tweet_text)
        print("reply", reply_text)
        # Reply to the mention
        client.create_tweet(in_reply_to_tweet_id=mention_id, text=reply_text)
    save_mentioned_tweets(mentioned_tweets)

    return f"last mentions id is {last_fetched_tweet_id}"


scheduler.add_job(id='Scheduled Task', func=fetch_tweets, trigger="interval", seconds=90)
scheduler.start()
