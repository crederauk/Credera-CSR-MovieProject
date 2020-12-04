import logging
import os
import sys

import tweepy

from movie_recommendation_engine import MovieRecommendationEngine
from movie_tweet_listener import MovieTweetListener

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
account_name = os.getenv("TWITTER_ACCOUNT_NAME")
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

valid_credentials = api.verify_credentials()
if not valid_credentials:
    logging.error("Error during authentication")
else:
    logging.info("Authentication successful")
    logging.info("MoviesRus Twitter bot started")

movie_recommendation_engine = MovieRecommendationEngine(tmdb_api_key=os.getenv("TMDB_API_KEY"))

movie_tweet_listener = MovieTweetListener(movie_recommendation_engine, api)

stream = tweepy.Stream(auth=api.auth, listener=movie_tweet_listener)
stream.filter(track=[account_name], is_async=True)
