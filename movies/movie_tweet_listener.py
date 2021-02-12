import logging
import random

import tweepy


class MovieTweetListener(tweepy.StreamListener):

    def __init__(self, movie_recommendation_engine, twitter_api):
        super().__init__()
        self.movie_recommendation_engine = movie_recommendation_engine
        self.twitter_api = twitter_api

    def on_status(self, status):
        logging.info(f"Received a Tweet!: {status.text}")
        try:
            movie_recommendations = self.movie_recommendation_engine.discover_movie_by_tweet(status.text)
            print(type(movie_recommendations))
            logging.info(f"Received {len(movie_recommendations)} recommendations, picking one at random")
            random_recommendation = random.choice(movie_recommendations)
            print(type(random_recommendation))
            print(random_recommendation)
            logging.info(f"Selected '{random_recommendation}'!")
            reply_text = f"@{status.author.name} You should try watching '{random_recommendation.original_title}'. Other people who watched it gave it an " \
                         f"average rating of {random_recommendation.vote_average}/10 "
            logging.info(f"Will tweet back: {reply_text}")
            self.twitter_api.update_status(status=reply_text,
                                           in_reply_to_status_id=status.id,
                                           auto_populate_reply_metadata=True)
        except Exception:
            logging.error("Could not obtain a movie recommendation for this Tweet")
