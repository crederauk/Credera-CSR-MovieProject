import logging
from typing import List

import requests
from tmdbv3api import Discover, TMDb


class MovieRecommendationEngine:
    def __init__(self, tmdb_api_key, base_api_url='https://api.themoviedb.org/', api_version=3):
        self.base_api_url = base_api_url
        self.api_version = api_version
        self.tmdb = TMDb()
        self.tmdb.api_key = tmdb_api_key
        self.discover = Discover()
        self.all_movie_genres = None

    def _get_genre_codes(self, genres: List[str]):
        all_genres = self._get_genres()
        genre_codes = []
        for genre in genres:
            matching_genre = next(filter(lambda g: g['name'].lower() == genre.lower(), all_genres))
            genre_codes.append(matching_genre['id'])
        return genre_codes

    def _get_genres(self):
        if self.all_movie_genres is None:
            logging.info("No movie genres cached, calling API...")
            genres_response = requests.get(
                f'{self.base_api_url}{self.api_version}/genre/movie/list?api_key={self.tmdb.api_key}&language=en-US')
            if genres_response.ok:
                all_movie_genres = genres_response.json()
                self.all_movie_genres = all_movie_genres['genres']
                return all_movie_genres['genres']
            else:
                logging.error("There was an error getting the list of movie genres")

        return self.all_movie_genres

    def is_valid_genre(self, genre: str):
        all_valid_genres = self._get_genres()
        if genre.lower() in [genre['name'].lower() for genre in all_valid_genres]:
            logging.debug(f"A film with a genre of '{genre}' is a valid genre")
            return True
        else:
            logging.debug(f"A film with a genre of '{genre}' is not a valid genre!")
            return False

    def discover_movie_by_genres(self, genres: List[str], original_language='en'):
        logging.info(f"Searching for movies of the following genres: {', '.join(genres)}")
        genre_codes = self._get_genre_codes(genres)
        recommendations = self.discover.discover_movies({
            'include_adult': False,
            'with_genres': ','.join([str(g) for g in genre_codes]),
            'sort_by': 'popularity.desc',
            'vote_average.gte': 7,
            'with_original_language': original_language
        })
        logging.info(f"Found the following movies: {recommendations}")
        return recommendations

    def _extract_genres_from_string(self, string):
        genres_in_input = []
        all_valid_genres = self._get_genres()
        all_valid_genre_names = [genre['name'].lower() for genre in all_valid_genres]
        for genre in all_valid_genre_names:
            if genre in string.lower():
                genres_in_input.append(genre)
        logging.info(f"Detected '{genres_in_input}' in '{string}'")
        return genres_in_input

    def discover_movie_by_tweet(self, tweet: str):
        genres = self._extract_genres_from_string(tweet)
        if len(genres) >= 1:
            recommendations = self.discover_movie_by_genres(genres)
        else:
            raise ValueError(f"No valid genres found in tweet with content: {tweet}")
        return recommendations
