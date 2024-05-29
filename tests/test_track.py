"""
This is the test file for Track class.
"""

import pytest
import requests
import json
from models.track import Track
from unittest.mock import patch

@pytest.fixture
def track():
    with patch('models.track.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = '{"access_token": "12345"}'.encode('utf-8')
        t = Track()
        return t

def test_track_class_attributes(track):
    assert track.username == 'kevinbjl' and track.client_id == 'a4f983ed7c344366a76acf06966729cc' and \
        track.client_secret == '687d6d3c127c4b6f94cb4011a2dd14f1' and track.redirect_url == 'http://localhost:8888' and \
        track.scope == 'user-library-read' and track.user_id == '31m5su2opjyjlt7agj5c3inbgjqq' and \
        track.token_url == 'https://accounts.spotify.com/api/token'

def test_get_auth_header_connection_error():
    with patch('models.track.requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        t = Track()
        assert t.headers is None

def test_get_auth_header_bad_status_code():
    with patch('models.track.requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        t = Track()
        assert t.headers is None

def test_get_auth_header_invalid_credentials():
    with pytest.raises(ValueError):
        with patch('models.track.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.content = '{"error": "error_message"}'.encode('utf-8')
            Track()

def test_get_auth_header_when_successful():
    with patch('models.track.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = '{"access_token": "12345"}'.encode('utf-8')
        t = Track()
        assert t.headers == {'Authorization': 'Bearer ' + '12345'}

def test_track_init(track):
    assert track.artist_data is None and track.track_data is None and \
        track.album_data is None and track.artist_info is None and \
        track.album_info is None and track.headers == {'Authorization': 'Bearer ' + '12345'} and \
        track.related_artists is None and track.list_of_related_artists is None and \
        track.top_tracks is None and track.dict_of_top_tracks is None and \
        track.track_audio_feature is None

def test_find_artist_raises_type_error(track):
    with pytest.raises(TypeError):
        track.find_artist(1975)

def test_find_artist_raises_value_error(track):
    with pytest.raises(ValueError):
        track.find_artist('')

def test_find_artist_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_artist('Deep Purple')
        assert track.artist_data is None

def test_find_artist_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_artist('Led Zeppelin')
        assert track.artist_data is None

def test_find_artist_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": []}}'.encode('utf-8')
            track.find_artist('Some non-existent artist')

def test_find_artist_when_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": [{"name": "Draft Pink"}]}}'.encode('utf-8')
            track.find_artist('Daft Punk')

def test_find_artist_when_successful(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '{"artists": {"items": [{"name": "Daft Punk"}]}}'.encode('utf-8')
        track.find_artist('Daft Punk')
        assert track.artist_data == json.loads(mock_get.return_value.content.decode('utf-8'))

def test_find_track_raises_type_error_under_wrong_track_input(track):
    with pytest.raises(TypeError):
        track.find_track(22, 'Taylor Swift')

def test_find_track_raises_type_error_under_wrong_artist_input(track):
    with pytest.raises(TypeError):
        track.find_track('About You', 1975)

def test_find_track_raises_value_error_under_wrong_track_input(track):
    with pytest.raises(ValueError):
        track.find_track('', 'R.E.M.')

def test_find_track_raises_value_error_under_wrong_artist_input(track):
    with pytest.raises(ValueError):
        track.find_track('Where Is my Mind?', '')

def test_find_track_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_track('Enter Sandman', 'Metallica')
        assert track.track_data is None

def test_find_track_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_track('Immigrant Song', 'Led Zeppelin')
        assert track.track_data is None

def test_find_track_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": []}}'.encode('utf-8')
            track.find_track('Some non-existent track', 'Some non-existent artist')

def test_find_track_when_artist_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Heaven", "artists": [{"name": "Lead Ziplin"}]}]}}'.encode('utf-8')
            track.find_track('Stairway to Heaven', 'Led Zeppelin')

def test_find_track_when_track_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Hell", "artists": [{"name": "Led Zeppelin"}]}]}}'.encode('utf-8')
            track.find_track('Stairway to Heaven', 'Led Zeppelin')

def test_find_track_when_both_results_do_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Hell", "artists": [{"name": "Lead Ziplin"}]}]}}'.encode('utf-8')
            track.find_track('Stairway to Heaven', 'Led Zeppelin')

def test_find_track_when_successful(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '{"tracks": {"items": [{"artists": [{"name": "Eric Clapton"}], "name": "Layla"}]}}'.encode('utf-8')
        track.find_track('Layla', 'Eric Clapton')
        assert track.track_data == json.loads(mock_get.return_value.content.decode('utf-8'))

def test_find_album_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_album('Moving Pictures', 'Rush')
        assert track.album_data is None

def test_find_album_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_album('2112', 'Rush')
        assert track.album_data is None

def test_find_album_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": []}}'.encode('utf-8')
            track.find_album('Some non-existent track', 'Some non-existent artist')

def test_find_album_when_artist_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Heaven", "artists": [{"name": "Lead Ziplin"}]}]}}'.encode('utf-8')
            track.find_album('Stairway to Heaven', 'Led Zeppelin')

def test_find_album_when_track_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Hell", "artists": [{"name": "Led Zeppelin"}]}]}}'.encode('utf-8')
            track.find_album('Stairway to Heaven', 'Led Zeppelin')

def test_find_album_when_both_results_do_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": [{"name": "Stairway to Hell", "artists": [{"name": "Lead Ziplin"}]}]}}'.encode('utf-8')
            track.find_album('Stairway to Heaven', 'Led Zeppelin')

def test_find_album_when_successful(track):
    with patch('models.track.Track.find_track') as mock_method:
        mock_method.side_effect = None
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"album_name": "Room on Fire"}'.encode('utf-8')
            track.track_data = {"tracks": {"items": [{"album": {"id": "12345"}}]}}
            track.find_album('Reptilia', 'The Strokes')
            assert track.album_data == json.loads(mock_get.return_value.content.decode('utf-8'))

def test_find_related_artist_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_related_artist('Deep Purple')
        assert track.related_artists is None

def test_find_related_artist_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_artist('Led Zeppelin')
        assert track.related_artists is None

def test_find_related_artist_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": []}}'.encode('utf-8')
            track.find_related_artist('Some non-existent artist')

def test_find_related_artist_when_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": [{"name": "Draft Pink"}]}}'.encode('utf-8')
            track.find_related_artist('Daft Punk')

def test_find_related_artist_when_successful(track):
    with patch('models.track.Track.find_artist') as mock_method:
        mock_method.side_effect = None
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"Related artist": ["Kansas"]}'.encode('utf-8')
            track.artist_data = {'artists': {'items': [{'id': '12345'}]}}
            track.find_related_artist('Rush')
            assert track.related_artists == json.loads(mock_get.return_value.content.decode('utf-8'))

def test_find_top_tracks_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_top_tracks('Deep Purple')
        assert track.top_tracks is None

def test_find_top_tracks_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_top_tracks('Led Zeppelin')
        assert track.top_tracks is None

def test_find_top_tracks_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": []}}'.encode('utf-8')
            track.find_top_tracks('Some non-existent artist')

def test_find_top_tracks_when_result_does_not_match_input(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"artists": {"items": [{"name": "Draft Pink"}]}}'.encode('utf-8')
            track.find_top_tracks('Daft Punk')

def test_find_top_tracks_when_successful(track):
    with patch('models.track.Track.find_artist') as mock_method:
        mock_method.side_effect = None
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"Top tracks": ["Tom Sawyer"]}'.encode('utf-8')
            track.artist_data = {'artists': {'items': [{'id': '12345'}]}}
            track.find_related_artist('Rush')
            assert track.related_artists == json.loads(mock_get.return_value.content)

def test_find_track_audio_feature_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.find_track_audio_feature('Smoke on the Water', 'Deep Purple')
        assert track.track_audio_feature is None

def test_find_track_audio_feature_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.find_track_audio_feature('Stairway to Heaven', 'Led Zeppelin')
        assert track.track_audio_feature is None

def test_find_track_audio_feature_when_nothing_is_found(track):
    with pytest.raises(ValueError):
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": {"items": []}}'.encode('utf-8')
            track.find_track_audio_feature('Some non-existent track', 'Some non-existent artist')

def test_find_track_audio_feature_when_successful(track):
    with patch('models.track.Track.find_track') as mock_method:
        mock_method.side_effect = None
        with patch('models.track.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = '{"tracks": "some audio feature"}'.encode('utf-8')
            track.track_data = {'tracks': {'items': [{'id': '12345'}]}}
            track.find_track_audio_feature('Layla', 'Eric Clapton')
            assert track.track_audio_feature == json.loads(mock_get.return_value.content.decode('utf-8'))

def test_extract_artist_info_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.extract_artist_info('Deep Purple')
        assert track.artist_info is None

def test_extract_artist_info_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.extract_artist_info('Led Zeppelin')
        assert track.artist_info is None

def test_extract_artist_info_when_successful(track):
    with patch('models.track.Track.find_artist') as mock_method:
        mock_method.side_effect = None
        track.artist_data = {"artists": {"items":
            [{"genres": "Alternative Rock",
            "external_urls": {"spotify": "spotify.com"},
            "id": "12345",
            "images": [{}, {"url": "img.com"}],
            "name": "Red Hot Chili Peppers",
            "popularity": "5"}]}}
        track.extract_artist_info('RHCP')
        assert track.artist_info == {
            'genre': 'Alternative Rock',
            'spotify_url': 'spotify.com',
            'id': '12345',
            'image': 'img.com',
            'name': 'Red Hot Chili Peppers',
            'popularity': '5'
        }

def test_extract_album_info_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.extract_album_info('Smoke on the Water', 'Deep Purple')
        assert track.album_info is None

def test_extract_album_info_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.extract_album_info('Here Comes your Man', 'Pixies')
        assert track.album_info is None

def test_extract_album_info_when_successful(track):
    with patch('models.track.Track.find_album') as mock_method:
        mock_method.side_effect = None
        track.album_data = {"artists": [{"name": "Rush", "id": "12345"}],
            "external_urls": {"spotify": "spotify.com"},
            "images": [{"url": "image.com"}],
            "label": "Anthem Records",
            "name": "Permanent Waves",
            "popularity": "5",
            "release_date": "1980/1/14",
            "total_tracks": "6",
            "tracks": {"items": [{"name": "The Spirit Of Radio"},
                                 {"name": "Freewill"},
                                 {"name": "Jacobs' Lader"},
                                 {"name": "Entre Nous"},
                                 {"name": "Different Nous"},
                                 {"name": "Natural Science"}]}}
        track.extract_album_info('Freewill', 'Rush')
        assert track.album_info == {
            'artist': 'Rush',
            'artist_id': '12345',
            'spotify_url': 'spotify.com',
            'image': 'image.com',
            'label': 'Anthem Records',
            'name': 'Permanent Waves',
            'popularity': '5',
            'release_date': '1980/1/14',
            'num_of_tracks': '6',
            'tracks': ["The Spirit Of Radio", "Freewill", "Jacobs' Lader",
                       "Entre Nous", "Different Nous", "Natural Science"]
        }

def test_extract_related_artist_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.extract_related_artist('Deep Purple')
        assert track.list_of_related_artists is None

def test_extract_related_artist_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.extract_related_artist('Pixies')
        assert track.list_of_related_artists is None

def test_extract_related_artist_when_successful(track):
    with patch('models.track.Track.find_related_artist') as mock_method:
        mock_method.side_effect = None
        track.related_artists = {'artists': [{'name': 'Kansas'}, {'name': 'Yes'}]}
        track.extract_related_artist('Rush')
        assert track.list_of_related_artists == ['Kansas', 'Yes']

def test_extract_top_tracks_connection_error(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        track.extract_top_tracks('Deep Purple')
        assert track.dict_of_top_tracks is None

def test_extract_top_tracks_bad_status_code(track):
    with patch('models.track.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        track.extract_top_tracks('Pixies')
        assert track.dict_of_top_tracks is None

def test_extract_top_tracks_when_successful(track):
    with patch('models.track.Track.find_top_tracks') as mock_method:
        mock_method.side_effect = None
        track.top_tracks = {'tracks': [{'name': 'Tom Sawyer', 'popularity': '80'}, {'name': 'Limelight', 'popularity': '65'}]}
        track.extract_top_tracks('Rush')
        assert track.dict_of_top_tracks == {'Tom Sawyer': '80', 'Limelight': '65'}