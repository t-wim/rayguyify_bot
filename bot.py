
import os, time, json, random, logging
import tweepy
import requests
from requests.exceptions import ConnectionError
from dotenv import load_dotenv
from meme_generator import generate

load_dotenv()

client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
    wait_on_rate_limit=True
)
auth_v1 = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)
api_v1 = tweepy.API(auth_v1)

BOT_USER_ID = int(os.getenv("BOT_USER_ID"))
BOT_HANDLE  = os.getenv("BOT_HANDLE", "rayguyify").lower()
PING        = int(os.getenv("PING_INTERVAL", "180"))
TOPICS      = json.load(open("topics.json"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def detect(text: str) -> str:
    t = text.lower()
    for topic, cfg in TOPICS.items():
        if any(k in t for k in cfg["keywords"]):
            return topic
    return random.choice(list(TOPICS))

def main():
    last_id = None
    logging.info("Starting bot loop with PING_INTERVAL=%d", PING)
    time.sleep(15)  # Delay at startup
    while True:
        try:
            resp = client.get_users_mentions(BOT_USER_ID, since_id=last_id, max_results=25)
            if resp.data:
                for m in reversed(resp.data):
                    txt = m.text.replace(f"@{BOT_HANDLE}", "").strip()
                    topic = detect(txt)
                    meme = generate(topic, txt)
                    media = api_v1.media_upload(meme)
                    user = client.get_user(id=m.author_id).data.username
                    client.create_tweet(in_reply_to_tweet_id=m.id,
                                        text=f"@{user} Here you go!",
                                        media_ids=[media.media_id])
                    logging.info("Replied to tweet %s with topic '%s'", m.id, topic)
                    last_id = m.id
        except tweepy.TooManyRequests:
            logging.warning("Rate limit hit. Sleeping for 15 minutes.")
            time.sleep(900)
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as neterr:
            logging.warning("Network error: %s → sleeping 5 min", neterr)
            time.sleep(300)
        except Exception as e:
            logging.error("Unexpected error: %s", e, exc_info=True)
            time.sleep(60)

        logging.info("Waiting %d seconds before next poll...", PING)
        time.sleep(PING)

if __name__ == "__main__":
    main()
