import os.path
from multiprocessing import Pool
from tweepy.streaming import StreamListener
import json

from bvs.database import db


def new_tweet(tweet):
    dump = json.dumps(tweet)

    pipe = db.pipeline()
    pipe.lpush('tweets', dump)
    pipe.ltrim('tweets', 0, 99);
    pipe.publish('tweet', dump)
    pipe.execute()

def update_tweet(tweet):
    pipe = db.pipeline()
    pipe.watch('tweets')
    tweets = pipe.lrange('tweets', 0, 99)
    pipe.multi()
    for i, t in enumerate(tweets):
        data = json.loads(t)
        if data['id'] == tweet['id']:
            pipe.lset('tweets', i, json.dumps(tweet))
            break
    pipe.execute()


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
