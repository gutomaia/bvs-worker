from __future__ import absolute_import
from unittest import TestCase
from mock import patch
from fakeredis import FakeStrictRedis
import json
import re
from faker import Factory

from bvs.twitter import new_tweet
import random

fake = Factory.create()



class TweetTest(TestCase):


    def setUp(self):
        self.redis_patcher = patch('bvs.twitter.db', new_callable=FakeStrictRedis)
        self.redis = self.redis_patcher.start()

    def tearDown(self):
        self.redis.flushall()
        self.redis_patcher.stop()

    def fixture_tweet(self, **kwargs):
        tid = random.randint(1000000, 9999999)
        tweet = dict(
            id = tid,
            user = fake.first_name(),
            picture = 'https://pbs.twimg.com/profile_images/%s/ef3de590b0e66bbf2ac644bd130e8424.png' % tid,
            msg = '%s BvS' % fake.text()[0:138],
            timestamp = 1231231,
        )
        tweet.update(kwargs)
        return tweet

    def constraint_no_tweets(self):
        self.assertEquals(0, len(self.redis.lrange('tweets', 0, 1000)))

    def assert_one_tweet(self):
        tweets = self.redis.lrange('tweets', 0, 100)
        self.assertEquals(1, len(tweets))
        return json.loads(tweets[0])


    def test_new_tweet(self):
        self.constraint_no_tweets()
        actual = self.fixture_tweet()

        new_tweet(actual)

        expected = self.assert_one_tweet()
        self.assertEquals(actual, expected)

    def test_positive_tweet_with_id_1337(self):
        self.constraint_no_tweets()
        actual = self.fixture_tweet(id=1337)

        new_tweet(actual)

        expected = self.assert_one_tweet()
        self.assertEquals(1337, expected['id'])

    def test_store_no_more_than_one_hundred_tweets(self):
        self.constraint_no_tweets()

        for i in range(150):
            new_tweet(self.fixture_tweet())

        tweets = self.redis.lrange('tweets', 0, 100)
        self.assertEquals(100, len(tweets))
