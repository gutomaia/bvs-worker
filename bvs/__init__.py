import os.path
from multiprocessing import Pool
from tweepy.streaming import StreamListener
from requests import post
import json

from bvs.alchemy import opinion
from bvs.twitter import update_tweet, new_tweet

pool = Pool(30)

class TweetListener(StreamListener):

    def __init__(self, alchemy_api_key):
        super(TweetListener, self).__init__()
        self.alchemy_api_key = alchemy_api_key

    def on_data(self, data):
        tweet = json.loads(data)

        data = dict(
            id = tweet['id'],
            user = tweet['user']['screen_name'],
            picture = tweet['user']['profile_image_url'],
            msg = tweet['text'],
            timestamp = tweet['timestamp_ms'],
        )
        print 'tweet', data

        pool.apply_async(opinion, args=(data, self.alchemy_api_key), callback=update_tweet)

        new_tweet(data)
        return True

    def on_error(self, status):
        print 'error', status
