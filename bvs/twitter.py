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
