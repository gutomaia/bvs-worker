import os.path
from multiprocessing import Pool
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from requests import post
import json
import redis

from os import environ as env

if 'VCAP_SERVICES' in env:
    vcap_services = json.loads(env['VCAP_SERVICES'])
    credentials = vcap_services['redis-2.6'][0]['credentials']
    host = credentials['host']
    port = credentials['port']
    password = credentials['password']
else:
    host = 'localhost'
    port = 6379
    password = None

r = redis.StrictRedis(host=host, port=port, password=password, db=0)

hashtag = 'BvS'

def notify_score():
    print'notify_score'

    pipe = r.pipeline()
    keys = ['positive', 'negative', 'neutral', 'error']
    for key in keys:
        pipe.get(key)
    values = pipe.execute()

    data = dict(zip(keys, values))

    r.publish('score', json.dumps(data))

def notify_opinion(tweet):
    print 'notify_opinion', tweet
    r.publish('opinion', json.dumps(tweet))

def opinion(tweet, api_key=False, hashtag=hashtag):
    if not api_key:
        return

    url = 'http://access.alchemyapi.com/calls/text/TextGetTargetedSentiment'

    params = dict(
        apikey=api_key,
        outputMode='json'
    )

    data = dict(text = tweet['msg'],
        target = hashtag
    )

    res = post(url, params=params, data=data)

    if res.status_code == 200:
        o = res.json()
        if o['status'] == 'OK':
            tweet['status'] = o['docSentiment']['type']
        elif o['status'] == 'ERROR':
            tweet['status'] = 'error'

    if 'status' not in tweet:
        tweet['status'] = 'unknow'

    r.incr(tweet['status'])
    print 'status', tweet['id'], tweet['status']

    notify_opinion(tweet)
    notify_score()
    return tweet

def new_tweet(data):
    dump = json.dumps(data)

    pipe = r.pipeline()
    pipe.lpush('tweets', dump)
    pipe.ltrim('tweets', 0, 99);
    pipe.publish('tweet', dump)
    pipe.execute()

def update_db(tweet):
    print 'update_db', tweet
    pipe = r.pipeline()
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

        pool.apply_async(opinion, args=(data, self.alchemy_api_key), callback=update_db)

        new_tweet(data)
        return True

    def on_error(self, status):
        print 'error', status


if __name__ == '__main__':
    print 'started worker'
    twitter_consumer_key = env.get('TWITTER_CONSUMER_KEY')
    twitter_consumer_secret = env.get('TWITTER_CONSUMER_SECRET')
    twitter_access_token = env.get('TWITTER_ACCESS_TOKEN')
    twitter_access_token_secret = env.get('TWITTER_ACCESS_TOKEN_SECRET')
    alchemy_api_key = env.get('ALCHEMY_API_KEY')

    if os.path.isfile('development.ini'):
        import ConfigParser, os
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
