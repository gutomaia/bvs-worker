from os import environ as env
import os

from bvs.twitter import TweetListener
from tweepy import OAuthHandler
from tweepy import Stream

hashtag = 'BvS'

print 'started worker'
twitter_consumer_key = env.get('TWITTER_CONSUMER_KEY')
twitter_consumer_secret = env.get('TWITTER_CONSUMER_SECRET')
twitter_access_token = env.get('TWITTER_ACCESS_TOKEN')
twitter_access_token_secret = env.get('TWITTER_ACCESS_TOKEN_SECRET')
alchemy_api_key = env.get('ALCHEMY_API_KEY')

if os.path.isfile('development.ini'):
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.readfp(open('development.ini'))

    twitter_consumer_key = config.get('twitter', 'consumer_key')
    twitter_consumer_secret = config.get('twitter', 'consumer_secret')
    twitter_access_token = config.get('twitter', 'access_token')
    twitter_access_token_secret = config.get('twitter', 'access_token_secret')
    alchemy_api_key = config.get('alchemy', 'api_key')


l = TweetListener(alchemy_api_key=alchemy_api_key)

auth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
stream = Stream(auth, l)
stream.filter(track=[hashtag])
