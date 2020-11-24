import logging
from unittest import TestCase
from unittest.mock import patch

from movie_recommendation_engine import MovieRecommendationEngine

TEST_API_KEY = 'TEST_API_KEY'
ALL_GENRES_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TEST_API_KEY}&language=en-US"

all_dummy_genres = {
    "genres": [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 16, "name": "Animation"}]}

genre_to_movies = {"Action": "Die hard", "Adventure": "Lord of the Rings", "Animation": "Spirited Away"}


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.ok = True

        def json(self):
            return self.json_data

    if args[0] == ALL_GENRES_URL:
        return MockResponse(all_dummy_genres, 200)

    return MockResponse(None, 404)


def _get_genre_name_by_id(genre_id):
    genre_name = ''
    for genre in all_dummy_genres['genres']:
        if genre_id == genre['id']:
            genre_name = genre['name']
    return genre_name


def mocked_discover_movies(args):
    genre_ids_requested = [int(requested_genre) for requested_genre in args['with_genres'].split(',')]
    valid_dummy_genre_ids = [genre['id'] for genre in all_dummy_genres['genres']]
    movies_to_return = []
    if set(genre_ids_requested).issubset(set(valid_dummy_genre_ids)):
        for genre_id in genre_ids_requested:
            genre_name = _get_genre_name_by_id(genre_id)
            movies_to_return.append(genre_to_movies.get(genre_name))
    return movies_to_return


class TestMovieRecommendationEngine(TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.movie_recommendation_engine = MovieRecommendationEngine(tmdb_api_key=TEST_API_KEY)

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_get_genres(self, mock_get):
        action_is_valid_genre = self.movie_recommendation_engine.is_valid_genre('Action')
        action_lowercase_is_valid_genre = self.movie_recommendation_engine.is_valid_genre('action')
        tv_is_valid_genre = self.movie_recommendation_engine.is_valid_genre('tv')

        self.assertTrue(action_is_valid_genre)
        self.assertTrue(action_lowercase_is_valid_genre)
        self.assertFalse(tv_is_valid_genre)
        self.assertEqual(1, mock_get.call_count, "API should only be called once (client should cache the result)")

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("tmdbv3api.objs.discover.Discover.discover_movies", side_effect=mocked_discover_movies)
    def test_discover_movie_by_genre(self, mock_get, mock_discover_movies):
        action_recommendation = self.movie_recommendation_engine.discover_movie_by_genres(['Action'])
        self.assertEqual(1, mock_discover_movies.call_count)
        self.assertEqual(1, mock_get.call_count, "API should only be called once (client should cache the result)")
        self.assertEqual(1, len(action_recommendation))
        self.assertEqual(genre_to_movies.get('Action'), action_recommendation[0])

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("tmdbv3api.objs.discover.Discover.discover_movies", side_effect=mocked_discover_movies)
    def test_discover_movie_by_tweet(self, mock_get, mock_discover_movies):
        string_containing_action = "Example input string containing the word action"
        string_containing_adventure = "Adventure!"
        string_containing_more_than_one_genre = "Action and Animation, please!"


        action_result = self.movie_recommendation_engine.discover_movie_by_tweet(string_containing_action)
        adventure_result = self.movie_recommendation_engine.discover_movie_by_tweet(string_containing_adventure)
        two_genre_result = self.movie_recommendation_engine.discover_movie_by_tweet(string_containing_more_than_one_genre)

        self.assertEqual(genre_to_movies.get('Action'), action_result[0])
        self.assertEqual(genre_to_movies.get('Adventure'), adventure_result[0])
        self.assertCountEqual(['Die hard', 'Spirited Away'], two_genre_result)

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_discover_movie_by_tweet_not_understood(self, mock_get):
        string_containing_no_genre = "Hello"
        self.assertRaises(ValueError, self.movie_recommendation_engine.discover_movie_by_tweet, string_containing_no_genre)
