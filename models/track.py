"""
This is the class file for track.
"""

import requests
import base64
import json
import difflib

SIMILARITY_THRESHOLD = 0.9    # Threshold for similarity score between two strings


class Track:
    """
    Data model for tracks.
    Information related to a track, including artist who composed it and album it belongs to, are also part of this class.
    The attributes are obtained from Spotify user dashboard.
    They're required for authorization of Spotify API.
    """

    # I've hidden my Spotify API credentials
    username = ''
    client_id = ''
    client_secret = ''
    redirect_url = ''
    scope = ''
    user_id = ''
    token_url = ''

    def __init__(self):
        """
        This is the constructor.
        The get_auth_header() method should always be invoked before doing anything else.
        """
        self.headers = None
        self.artist_data = None
        self.track_data = None
        self.album_data = None
        self.track_audio_feature = None
        self.artist_info = None
        self.album_info = None
        self.related_artists = None
        self.list_of_related_artists = None
        self.top_tracks = None
        self.dict_of_top_tracks = None
        try:
            self.get_auth_header()
        except requests.exceptions.ConnectionError as ex:
            print(ex)

    def get_auth_header(self):
        """
        Function:
            Gets the authorization header for Spotify API.
        Parameters:
            None
        Return value:
            None
        """
        # This code is adapted from https://www.youtube.com/watch?v=WAmEZBEeNmg
        # Author: https://www.youtube.com/@AkamaiDeveloper
        auth_string = self.client_id + ':' + self.client_secret
        # Encode into bytes
        auth_bytes = auth_string.encode('utf-8')
        # Convert the bytes into a base64 encoded string, which is a format required by HTTP server
        auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

        headers = {'Authorization': 'Basic ' + auth_base64,
                   'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'client_credentials'}
        try:
            response = requests.post(self.token_url, headers=headers, data=data)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        if 'error' in response_json:
            raise ValueError('Invalid credentials.')
        token = response_json['access_token']
        self.headers = {'Authorization': 'Bearer ' + token}

    def find_artist(self, artist):
        """
        Function:
            Finds related information about an artist.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        if not isinstance(artist, str):
            raise TypeError('Artist name must be a string.')
        if artist == '':
            raise ValueError('Artist name cannot be an empty string.')

        url = 'https://api.spotify.com/v1/search'
        word_lst = []
        for word in artist.split(' '):
            word_lst.append(word)
        artist_name = '+'.join(word_lst)
        query = f'?q={artist_name}&type=artist&limit=1'
        query_url = url + query

        try:
            response = requests.get(query_url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.artist_data = response_json
        # The code below handles input error, when no related track or artist can be found, or something is found but does not quite match.
        if self.artist_data['artists']['items'] == [] or \
            difflib.SequenceMatcher(None, artist.lower(), self.artist_data['artists']['items'][0]['name'].lower()).ratio() < SIMILARITY_THRESHOLD:
            raise ValueError('Track or artist cannot be found.')

    def find_track(self, track, artist):
        """
        Function:
            Finds the related information about a track.
        Parameters:
            track: name of the track
            artist: name of the artist who composed the track
        Return value:
            None
        """
        if not isinstance(track, str) or not isinstance(artist, str):
            raise TypeError('Track name or artist name should be a string.')
        if track == '' or artist == '':
            raise ValueError('Track name or artist name should not be an empty string.')

        url = 'https://api.spotify.com/v1/search'
        word_lst = []
        for word in (track + ' ' + artist).split(' '):
            word_lst.append(word)
        track_name = '+'.join(word_lst)
        query = f'?q={track_name}&type=track&limit=1'
        query_url = url + query

        try:
            response = requests.get(query_url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return

        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.track_data = response_json
        # The code below handles input error, when no related track or artist can be found, or something is found but does not quite match.
        if self.track_data['tracks']['items'] == [] or \
            difflib.SequenceMatcher(None, artist.lower(), self.track_data['tracks']['items'][0]['artists'][0]['name'].lower()).ratio() < SIMILARITY_THRESHOLD:
            raise ValueError('Track or artist cannot be found.')
        # Many popular tracks from 90s or earlier will have something like  '- Remastered' in its name on Spotify, e.g. 'Stairway to Heaven - Remaster'.
        # This needs to be deleted, so that string matching is more accurate.
        else:
            spotify_track_name = self.track_data['tracks']['items'][0]['name']
            if ' - ' in spotify_track_name:
                spotify_track_name = spotify_track_name.split(' - ')[0]
            if difflib.SequenceMatcher(None, track.lower(), spotify_track_name.lower()).ratio() < SIMILARITY_THRESHOLD:
                raise ValueError('Track or artist cannot be found.')

    def find_album(self, track, artist):
        """
        Function:
            Finds the related information of an album that a track belongs to.
        Parameters:
            track: name of the track
            artist: name of the artist who composed the track
        Return value:
            None
        """
        self.find_track(track, artist)
        if self.track_data is None:
            return
        album_id = self.track_data['tracks']['items'][0]['album']['id']
        url = f'https://api.spotify.com/v1/albums/{album_id}'

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.album_data = response_json

    def find_related_artist(self, artist):
        """
        Function:
            Finds artists that are related to the artist the user searches for.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        self.find_artist(artist)
        if self.artist_data is None:
            return
        artist_id = self.artist_data['artists']['items'][0]['id']
        url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.related_artists = response_json

    def find_top_tracks(self, artist):
        """
        Function:
            Finds an artist's most popular tracks on Spotify.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        self.find_artist(artist)
        if self.artist_data is None:
            return
        artist_id = self.artist_data['artists']['items'][0]['id'] 
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=ES'

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.top_tracks = response_json

    def find_track_audio_feature(self, track, artist):
        """
        Function:
            Finds the audio features of a track.
        Parameters:
            track: name of the track
            artist: name of the artist who composed the track
        Return value:
            None
        """
        self.find_track(track, artist)
        if self.track_data is None:
            return
        track_id = self.track_data['tracks']['items'][0]['id']
        url = f'https://api.spotify.com/v1/audio-features/{track_id}'

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return
        if response.status_code != 200:
            return
        response_json = json.loads(response.content)
        self.track_audio_feature = response_json

    def extract_artist_info(self, artist):
        """
        Function:
            Extracts the information about the artist.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        self.find_artist(artist)
        if self.artist_data is None:
            return
        dict = {}
        dict['genre'] = self.artist_data['artists']['items'][0]['genres']
        dict['spotify_url'] = self.artist_data['artists']['items'][0]['external_urls']['spotify']
        dict['id'] = self.artist_data['artists']['items'][0]['id']
        dict['image'] = self.artist_data['artists']['items'][0]['images'][1]['url']
        dict['name'] = self.artist_data['artists']['items'][0]['name']
        dict['popularity'] = self.artist_data['artists']['items'][0]['popularity']
        self.artist_info = dict

    def extract_album_info(self, track, artist):
        """
        Function:
            Extracts the information about the album.
        Parameters:
            track: name of the track
            artist: name of the artist who composed the track
        Return value:
            None
        """
        self.find_album(track, artist)
        if self.album_data is None:
            return
        dict = {}
        dict['artist'] = self.album_data['artists'][0]['name']
        dict['artist_id'] = self.album_data['artists'][0]['id']
        dict['spotify_url'] = self.album_data['external_urls']['spotify']
        dict['image'] = self.album_data['images'][0]['url']
        dict['label'] = self.album_data['label']
        dict['name'] = self.album_data['name']
        dict['popularity'] = self.album_data['popularity']
        dict['release_date'] = self.album_data['release_date']
        dict['num_of_tracks'] = self.album_data['total_tracks']
        tracks = []
        for track in self.album_data['tracks']['items']:
            tracks.append(track['name'])
        dict['tracks'] = tracks
        self.album_info = dict

    def extract_related_artist(self, artist):
        """
        Function:
            Extracts the names of the related artists.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        self.find_related_artist(artist)
        if self.related_artists is None:
            return
        lst = []
        for artist in self.related_artists['artists']:
            lst.append(artist["name"])
        self.list_of_related_artists = lst

    def extract_top_tracks(self, artist):
        """
        Function:
            Extracts the top tracks.
        Parameters:
            artist: name of the artist
        Return value:
            None
        """
        self.find_top_tracks(artist)
        if self.top_tracks is None:
            return
        dict = {}
        for track in self.top_tracks['tracks']:
            dict[f'{track["name"]}'] = track['popularity']
        self.dict_of_top_tracks = dict
