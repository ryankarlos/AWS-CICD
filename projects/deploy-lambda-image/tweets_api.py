import tweepy
import time
import json
import boto3


def tweepy_search_api(
    event, consumer_key, consumer_secret, access_token, access_secret
):

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_secret
    )
    start_time = time.time()
    time_limit = event["duration"]
    api = tweepy.API(auth, wait_on_rate_limit=True)
    counter = 0
    for tweet in tweepy.Cursor(
        api.search_tweets, event.get("keyword"), count=100, tweet_mode="extended"
    ).items():
        if time.time() - start_time > time_limit:
            api.session.close()
            print(f"\n {time_limit} seconds time limit reached, so disconneting stream")
            print(f" {counter} tweets streamed ! \n")
            return
        else:
            if not tweet.full_text.startswith("RT"):
                counter += 1
                dt = tweet.created_at
                payload = {
                    "day": dt.day,
                    "month": dt.month,
                    "year": dt.year,
                    "time": dt.time().strftime("%H:%M:%S"),
                    "handle": tweet.user.screen_name,
                    "text": tweet.full_text,
                    "favourite_count": tweet.user.favourites_count,
                    "retweet_count": tweet.retweet_count,
                    "retweeted": tweet.retweeted,
                    "followers_count": tweet.user.followers_count,
                    "friends_count": tweet.user.friends_count,
                    "location": tweet.user.location,
                    "lang": tweet.user.lang,
                }
                print(f"{payload}")
