from main_tweepy import handler
import configparser

config = configparser.ConfigParser()
config.read("twitter_conf.ini")
consumer_key = config['DEFAULT']['APIKey']
consumer_secret = config['DEFAULT']['APIKeySecret']
access_token = config['DEFAULT']['AccessToken']
access_secret = config['DEFAULT']['AccessTokenSecret']
event = {'keyword': 'machine learning', 'delivery': 'stream'}
context = {}

handler(event, context)