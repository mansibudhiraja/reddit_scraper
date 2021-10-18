# reddit_scraper
reddit scraper

Reddit scraper to find keywords related to ente.io and notify telegram group for the keyword mention.

How to get a telegram group token
1. create a bot using BotFather.
2. create a group with the bot and promote it as an admin.
3. getUpdates Api call to and find the chat_id for the group where we want to send the notiofications.
4. send message api call to send group notification.


How to get reddit client secrets:
1. used the PRAW that provides a simple access to Reddit API.
2. We need an application id and secret so Reddit knows your application.
3. Authenticate via Oauth2 - https://github.com/reddit-archive/reddit/wiki/OAuth2
4. use Praw to get the latest comments and submissions.
5. Store the last scraped timestamp each time as a checkpoint and only query new submissions
6: Pass list of subreddits and keywords as command Line arguments
   
Run the script:
1. used argparse to parse the CLI.
2. pass argument as: python3 reddit_bot.py -sub "subredditname1" -search "keyword1"


config.ini:
[KEYS]
telegram_key= user_telegram_key
client_id= reddit_client_id
secret_key=reddit_secret_key
username=reddit_username
password=reddit_password




