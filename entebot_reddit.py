import praw
import requests
import json
from datetime import timezone, datetime
import configparser

def get_json_from_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js


def telegram_group(form, subreddit, permalink, content):
    BOT_TOKEN = telegram_key
    updates_url = "https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN)
    url = "https://www.reddit.com" + permalink

    # to check the chatID for the group
    # all_messages = get_json_from_url(updates_url)
    chat_id = "-541426392"
    message = 'Type: {} \nsubreddit: {} \n\nurl: {} \n\ncontent: {}'.format(form, subreddit, url, content)
    message_url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(BOT_TOKEN, chat_id, message)
    get_json_from_url(message_url)


def process_submission(all_posts):
    search_list = ["enteio", "ente.io", "photos", "privacy"]

    if "title" in vars(all_posts):
        normalized_text = all_posts.title.lower()
        type_post ="submission"
    if "body" in vars(all_posts):
        normalized_text = all_posts.body.lower()
        type_post = "comment"

    for word in search_list:
        if word in normalized_text:
            telegram_group(type_post, all_posts.subreddit, all_posts.permalink, normalized_text)
    return

def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results


cfg = configparser.ConfigParser()
cfg.read('example.ini')

client_id = cfg.get('KEYS', "client_id")
secret_key = cfg.get('KEYS', "secret_key")
username = cfg.get('KEYS', "username")
password = cfg.get('KEYS', "password")
telegram_key = cfg.get('KEYS', "telegram_key")

reddit = praw.Reddit(
    user_agent="my user agent",
    client_id=client_id,
    client_secret=secret_key,
    username=username,
    password=password,
)

subreddit = reddit.subreddit("testmansi+privacy+privacytoolsIO+degoogle")
stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

stack = []
if not stack:
    time_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    stack.append(time_now)
last_timestamp = stack.pop()

for post in stream:
    if last_timestamp > post.created_utc:
        process_submission(post)
stack.append(datetime.now().replace(tzinfo=timezone.utc).timestamp())








