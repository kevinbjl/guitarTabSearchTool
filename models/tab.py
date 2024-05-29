"""
This is the class file for tab.
"""

import requests
import difflib

SIMILARITY_THRESHOLD = 0.9    # Threshold for similarity score between two strings


class Tab:
    """
    Data model for guitar tabs.
    """
    def __init__(self):
        """
        This is the constructor.
        """
        self.tab_url = None
        self.track_name = None
        self.artist_name = None
        self.artist_data = None
        self.artist_tracks = None

    def fetch_by_track(self, track, artist):
        """
        Function:
            Fetches the url of a guitar tab by track name and artist.
        Parameters:
            track: name of the track
            artist: name of the artist
        Return value:
            None
        The query finds the best match. If no match can be found, it'll return the url of the omepage.
        """
        if not isinstance(track, str) or not isinstance(artist, str):
            raise TypeError('Track name or artist name should be a string.')
        if track == '' or artist == '':
            raise ValueError('Track name or artist name should not be an empty string.')
        url = 'http://www.songsterr.com/a/wa/bestMatchForQueryString'
        params = {'s': track, 'a': artist}
        try:
            response = requests.get(url, params=params)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        if response.url == 'https://www.songsterr.com/':
            # This means that no match can be found. It's treated as invalid input.
            raise ValueError('Track or artist cannot be found.')
        self.tab_url = response.url
        self.track_name = track

    def fetch_by_artist(self, artist):
        """
        Function:
            Fetches a json containing all the data related to a specified artist.
        Parameters:
            artist: name of the artist
        Return value:
            A list containing the data. If no match can be found, it'll return an empty list.
        """
        if not isinstance(artist, str):
            raise TypeError('Artist name should be a string.')
        if artist == '':
            raise ValueError('Artist name should not be an empty string.')
        self.artist = artist
        s = []
        for word in artist.split(' '):
            s.append(word)
        artist_name = ','.join(s)
        artist_name = ''.join([char for char in artist_name if char != "'"])
        url = 'http://www.songsterr.com/a/ra/songs/byartists.json'
        params = {'artists': artist_name}
        try:
            response = requests.get(url, params=params)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        if response.json() == []:
            raise ValueError('Artist cannot be found.')
        self.artist_data = response.json()
        self.artist_name = artist

    def filter_artist_data(self):
        """
        Function:
            Filters the artist data by fuzzy match.
        Parameters:
            None
        Return value:
            None
        """
        fuzzy_match_data = []
        string_to_match = self.artist_name.removeprefix('the')
        string_to_match = string_to_match.removeprefix('The')
        while string_to_match.startswith(' '):
            string_to_match = string_to_match[1:]
        string_to_match = string_to_match.lower()
        for dict in self.artist_data:
            score = difflib.SequenceMatcher(None, string_to_match, dict['artist']['nameWithoutThePrefix'].lower()).ratio()
            if score >= SIMILARITY_THRESHOLD:
                fuzzy_match_data.append(dict)
        self.artist_data = fuzzy_match_data

    def extract_artist_tracks(self):
        """
        Function:
            Extracts from the artist dataset a list of tracks that have available tabs.
        Parameters:
            None
        Return value:
            None
        """
        tracks = []
        if self.artist_data is None or self.artist_data == []:
            raise ValueError('Artist cannot be found.')
        else:
            for dict in self.artist_data:
                tracks.append(dict['title'])
            self.artist_tracks = list(set(tracks))
            self.artist_tracks.sort()
