import os.path
from requests import post
import json

from bvs.database import db

hashtag = 'BvS'

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

    db.incr(tweet['status'])
    print 'status', tweet['id'], tweet['status']

    notify_opinion(tweet)
    notify_score()
    return tweet


def notify_score():
    pipe = db.pipeline()
    keys = ['positive', 'negative', 'neutral', 'error']
    for key in keys:
        pipe.get(key)
    values = pipe.execute()

    data = dict(zip(keys, values))

    db.publish('score', json.dumps(data))

def notify_opinion(tweet):
    print 'notify_opinion', tweet
    db.publish('opinion', json.dumps(tweet))
