"""
This is the test file for Tab class.
"""

import pytest
import requests
from models.tab import Tab
from unittest.mock import patch

@pytest.fixture
def tab():
    t = Tab()
    return t

def test_tab_init(tab):
    assert tab.tab_url is None and tab.track_name is None and \
        tab.artist_data is None and tab.artist_tracks is None and \
        tab.artist_name is None

def test_fetch_by_track_raises_type_error_under_wrong_track_input(tab):
    with pytest.raises(TypeError):
        tab.fetch_by_track(22, 'Taylor Swift')

def test_fetch_by_track_raises_type_error_under_wrong_artist_input(tab):
    with pytest.raises(TypeError):
        tab.fetch_by_track('About You', 1975)

def test_fetch_by_track_raises_value_error_under_wrong_track_input(tab):
    with pytest.raises(ValueError):
        tab.fetch_by_track('', 'R.E.M.')

def test_fetch_by_track_raises_value_error_under_wrong_artist_input(tab):
    with pytest.raises(ValueError):
        tab.fetch_by_track('Where Is my Mind?', '')

def test_fetch_by_track_raises_value_error_when_track_or_artist_cannot_be_found(tab):
    with pytest.raises(ValueError):
        with patch('models.tab.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.url = 'https://www.songsterr.com/'
            tab.fetch_by_track('some non-existent track', 'or some non-existent track')

def test_fetch_by_track_server_failed(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        tab.fetch_by_track('Wake Up', 'Arcade Fire')
        assert tab.tab_url is None and tab.track_name is None

def test_fetch_by_track_bad_status_code(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        tab.fetch_by_track('Lullaby', 'The Cure')
        assert tab.tab_url is None and tab.track_name is None

def test_fetch_by_track_fetches_url_when_successful(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.url = 'https://google.com'
        tab.fetch_by_track('Paranoid', 'Black Sabbath')
        assert tab.tab_url == 'https://google.com'

def test_fetch_by_track_assigns_track_name_when_successful(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.url = 'https://google.com'
        tab.fetch_by_track('Thunderstruck', 'AC/DC')
        assert tab.track_name == 'Thunderstruck'

def test_fetch_by_artist_raises_type_error_under_wrong_artist_input(tab):
    with pytest.raises(TypeError):
        tab.fetch_by_artist(1975)

def test_fetch_by_artist_raises_value_error_under_wrong_artist_input(tab):
    with pytest.raises(ValueError):
        tab.fetch_by_artist('')

def test_fetch_by_artist_raises_value_error_when_artist_cannot_be_found(tab):
    with pytest.raises(ValueError):
        with patch('models.tab.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []
            tab.fetch_by_artist('some non-existent artist')

def test_fetch_by_artist_server_failed(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        tab.fetch_by_artist('Blur')
        assert tab.artist_data is None and tab.artist_name is None

def test_fetch_by_artist_bad_status_code(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        tab.fetch_by_artist('Oasis')
        assert tab.artist_data is None and tab.artist_name is None

def test_fetch_by_artist_fetches_data_when_successful(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            'artist': 'name'
        }]
        tab.fetch_by_artist('Cream')
        assert tab.artist_data == [{'artist': 'name'}]

def test_fetch_by_artist_assigns_artist_name_when_successful(tab):
    with patch('models.tab.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            'artist': 'name'
        }]
        tab.fetch_by_artist('Red Hot Chili Peppers')
        assert tab.artist_name == 'Red Hot Chili Peppers'

def test_filter_artist_data_with_no_prefix():
    # This is for testing string fuzzy match
    tab = Tab()
    tab.artist_name = 'Dire Straits'
    tab.artist_data = [{'artist': {'nameWithoutThePrefix': 'Dire Straits'}},
                       {'artist': {'nameWithoutThePrefix': 'Dire Strauts'}},
                       {'artist': {'nameWithoutThePrefix': 'dire strait'}},
                       {'artist': {'nameWithoutThePrefix': 'dire_straits'}},
                       {'artist': {'nameWithoutThePrefix': 'Dirr Sttaats'}}]
    tab.filter_artist_data()
    assert tab.artist_data == [{'artist': {'nameWithoutThePrefix': 'Dire Straits'}},
                       {'artist': {'nameWithoutThePrefix': 'Dire Strauts'}},
                       {'artist': {'nameWithoutThePrefix': 'dire strait'}},
                       {'artist': {'nameWithoutThePrefix': 'dire_straits'}}]

def test_filter_artist_data_with_prefix(tab):
    # This is for testing string fuzzy match
    tab = Tab()
    tab.artist_name = 'The Rolling Stones'
    tab.artist_data = [{'artist': {'nameWithoutThePrefix': 'Rolling Stones'}},
                       {'artist': {'nameWithoutThePrefix': 'Rooling Stones'}},
                       {'artist': {'nameWithoutThePrefix': 'roling stone'}},
                       {'artist': {'nameWithoutThePrefix': 'Roling_stoonr'}}]
    tab.filter_artist_data()
    assert tab.artist_data == [{'artist': {'nameWithoutThePrefix': 'Rolling Stones'}},
                       {'artist': {'nameWithoutThePrefix': 'Rooling Stones'}},
                       {'artist': {'nameWithoutThePrefix': 'roling stone'}}]

def test_extract_artist_tracks_sorted(tab):
    tab.artist_data = [{'title': 'Sultans of Swing'},
                       {'title': 'Walk of Life'},
                       {'title': 'Money for Nothing'}]
    tab.extract_artist_tracks()
    assert tab.artist_tracks == ['Money for Nothing', 'Sultans of Swing', 'Walk of Life']

def test_extract_artist_tracks_with_duplicate(tab):
    tab.artist_data = [{'title': 'Sultans of Swing'},
                       {'title': 'Walk of Life'},
                       {'title': 'Money for Nothing'},
                       {'title': 'Sultans of Swing'}]
    tab.extract_artist_tracks()
    assert tab.artist_tracks == ['Money for Nothing', 'Sultans of Swing', 'Walk of Life']

def test_extract_artist_tracks_when_empty(tab):
    with pytest.raises(ValueError):
        tab.artist_data = []
        tab.extract_artist_tracks()
