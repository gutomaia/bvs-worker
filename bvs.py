import os.path
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
    positive = r.get('positive')
    negative = r.get('negative')
    neutral = r.get('neutral')
    error = r.get('error')
    data = dict(
        positive=positive,
        negative=negative,
        neutral=neutral,
        error=error
    )
    dump = json.dumps(data)
    print dump
    r.publish('score', dump)


def opinion(tweet, api_key=False, hashtag=hashtag):

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
        opinion = res.json()
        print 'opinion', opinion
        if opinion['status'] == 'OK':
            tweet['status'] = opinion['docSentiment']['type']
        elif opinion['status'] == 'ERROR':
            tweet['status'] = 'error'

    if 'status' not in tweet:
        tweet['status'] = 'unknow'

    r.incr(tweet['status'])
    print 'status', tweet['id'], tweet['status']
    notify_score()



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

        opinion(data, self.alchemy_api_key)

        print data

        dump = json.dumps(data)

        r.lpush('tweets', dump)
        r.ltrim('tweets', 0, 99);
        r.publish('tweet', dump)

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
