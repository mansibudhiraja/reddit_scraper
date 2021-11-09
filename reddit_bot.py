import praw
import requests
import json
from datetime import timezone, datetime
import configparser
import os
import argparse
import sys
import re
import traceback
import logging
import logging.handlers as handlers
import time

logger = logging.getLogger('reddit')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler = handlers.TimedRotatingFileHandler('/tmp/normal.log', when='M', interval=1440, backupCount=0)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)

errorLogHandler = handlers.RotatingFileHandler('/tmp/error.log', maxBytes=5000, backupCount=0)
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(formatter)

logger.addHandler(logHandler)
logger.addHandler(errorLogHandler)

def get_json_from_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js


def notify_telegram_group(form, subreddit, permalink, content):
    BOT_TOKEN = telegram_key
    updates_url = "https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN)
    url = "https://www.reddit.com" + permalink

    # extract chat_id for the group where you want to send the notifications from get_updates api call
    # all_messages = get_json_from_url(updates_url)
    # print(all_messages)
    chat_id = "-638366714"
    message = 'Type: {} \nsubreddit: {} \n\nurl: {} \n\ncontent: {}'.format(form, subreddit, url, content)
    message_url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(BOT_TOKEN, chat_id, message)
    get_json_from_url(message_url)


def process_submission(all_posts):
    unique_posts = {}
    normalized_text = []
    if "title" in vars(all_posts):
        if "selftext" in vars(all_posts):   
            normalized_text.append(all_posts.selftext.lower())
        normalized_text.append(all_posts.title.lower())
        type_post ="submission"
    if "body" in vars(all_posts):
        normalized_text.append(all_posts.body.lower())
        type_post = "comment"

 
    for word in search_list:
        pattern = r'\b' + word + r'\b'
        for text in normalized_text:
            if re.search(pattern, text):
                if text not in unique_posts:
                    unique_posts[text] = 1
                    notify_telegram_group(type_post, all_posts.subreddit, all_posts.permalink, text)
    last_timestamp = datetime.now(timezone.utc)
    set_last_sync_time(filename, last_timestamp)
    return

def get_submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    logger.info("Fetched %d submissions and comments", len(results)) 
    if len(results)>0:
        logger.info("First entry created timestamp %s", str(results[0]))
    return results


def set_last_sync_time(filename, last_timestamp_datetime):
    local_last_timestamp = last_timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
    details = {'last_timestamp': local_last_timestamp}
    file = open(filename, "w")
    file.write(json.dumps(details))
    file.close()
    logger.info("Updated last sync time %s",local_last_timestamp)

def get_last_sync_time(filename):
    if not os.path.exists(filename):
        return datetime.now(timezone.utc)
    with open(filename, 'r') as file:
        data = file.read()
        js = json.loads(data)
        last_timestamp_datetime_format = datetime.strptime(js["last_timestamp"], '%Y-%m-%d %H:%M:%S')
    logger.info("Fetched Last sync time from file: %s", str(last_timestamp_datetime_format))
    return last_timestamp_datetime_format


try:
    path_current_directory = os.path.dirname(__file__)
    path_config_file = os.path.join(path_current_directory, 'config.ini')
    cfg = configparser.ConfigParser()
    cfg.read(path_config_file)

    client_id = cfg.get('KEYS', "client_id")
    secret_key = cfg.get('KEYS', "secret_key")
    username = cfg.get('KEYS', "username")
    password = cfg.get('KEYS', "password")
    telegram_key = cfg.get('KEYS', "telegram_key")

    reddit = praw.Reddit(
        user_agent="keyword",
        client_id=client_id,
        client_secret=secret_key,
        username=username,
        password=password,
    )


    try:
        parser = argparse.ArgumentParser("add subreddits & search words, example: -subreddit -search \n")
        parser.add_argument("-subreddit", type=str, nargs='+', help="add subreddits to search", dest="subreddit_list")
        parser.add_argument("-search", type=str, nargs='+', help="add words to search", dest="search_list")
        args = parser.parse_args()
        subreddit_list = "+".join(args.subreddit_list)
        search_list = args.search_list
    except:
        e = sys.exc_info()
        logger.error(e)


    subreddit = reddit.subreddit(subreddit_list)
    logger.info("Sucesssfully fetched subreddit")
    stream = praw.models.util.stream_generator(lambda **kwargs: get_submissions_and_comments(subreddit, **kwargs))
    logger.info("Fetched comments successfully")
    path_current_directory = os.path.dirname(__file__)
    filename = os.path.join(path_current_directory, 'last_sync_timestamp.txt')

    # set the last_sync_time for the ist run
    if not os.path.exists(filename):
        last_timestamp = datetime.now(timezone.utc)
        set_last_sync_time(filename, last_timestamp)
        logger.info("Successfully added last sync time for the first run")


    last_timestamp_dateformat = get_last_sync_time(filename)
    last_timestamp = last_timestamp_dateformat.replace(tzinfo=timezone.utc).timestamp()  ## convert to UTC

    for post in stream:
        if last_timestamp < post.created_utc:
            process_submission(post)

except Exception:
    logger.error(traceback.print_exc())

