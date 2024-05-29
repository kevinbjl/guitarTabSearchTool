"""
This is the driver file.
"""

import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
import streamlit as st
from models.tab import Tab
from models.track import Track

COMPENSATE = 10   # This is for mapping popularity from [0, 100] to [1, 5]
FILENAME = 'my_favourite.txt'    # Name of the file that stores favourite tracks
WIDTH = 600    # This is for tuning width of the displayed DataFrame

# Below are helper functions
def save_to_file(line):
    """
    Function:
        Saves a track to a file.
    Parameters:
        line: one line of input that contains the name of the track and the name of the artist
    Return value:
        None
    """
    with open(FILENAME, 'a') as file:
        file.write(line)


def remove_from_file(track):
    """
    Function:
        Removes a track from a file.
    Parameters:
        track: name of the track the user wants to remove
    Return value:
        None
    """
    with open(FILENAME, 'r') as file:
        lines = file.readlines()
    with open(FILENAME, 'w') as file:
        for line in lines:
            if line.strip('\n').split(', ')[0] != track:
                file.write(line)


def clear_file():
    """
    Function:
        Clears the file.
    Parameters:
        None
    Return value:
        None
    """
    with open(FILENAME, 'w') as file:
        file.write('')


def convert_key(key: int) -> str:
    """
    Function:
        Converts key to a human-readable string.
    Parameters:
        key: key of the track as an integer
    Return value:
        Key of the track as a string.
    """
    if key == 0:
        return 'C'
    elif key == 1:
        return 'C♯ / D♭'
    elif key == 2:
        return 'D'
    elif key == 3:
        return 'D♯ / E♭'
    elif key == 4:
        return 'E'
    elif key == 5:
        return 'F'
    elif key == 6:
        return 'F♯ / G♭'
    elif key == 7:
        return 'G'
    elif key == 8:
        return 'G♯ / A♭'
    elif key == 9:
        return 'A'
    elif key == 10:
        return 'A♯ / B♭'
    elif key == 11:
        return 'B'
    else:
        return 'No key is detected.'


def convert_mode(mode: int) -> str:
    """
    Function:
        Converts mode to a human-readable string.
    Parameters:
        mode: mode of the track as an integer
    Return value:
        Mode of the track as a string.
    """
    if mode == 1:
        return 'Major'
    else:
        return 'Minor'


def convert_time_signature(time_signature: int) -> str:
    """
    Function:
        Converts time signature to a human-readable string.
    Parameters:
        time_signature: time_signature of the track as an integer
    Return value:
        Time signature of the track as a string.
    """
    return str(time_signature) + ' / ' + str(4)


def convert_popularity(pop: int) -> str:
    """
    Function:
        Converts popularity from numeric value to a string.
        The level of popularity is indicated by the number of the 'fire' emojis.
    Parameters:
        pop: popularity as an integer
    Return value:
        A string containing emojis
    """
    return ":fire:" * (int(str(pop + COMPENSATE)[:-1]) // 2)


def main():
    """
    This is the main function.
    """
    track = Track()
    tab = Tab()
    st.title(':the_horns: :guitar: Guitar Tab Lookup Tool :guitar: :the_horns:')
    options = ['Search for guitar tab', 'Search for artist', 'My Favourite']
    # Integrate different functions into a sidebar
    response = st.sidebar.radio('Select a function', options)

    # Function choosen is to search for tab
    if response == options[0]:
        track_name = st.text_input('Enter name of the track')
        artist_name = st.text_input('Enter name of the artist')

        if track_name and artist_name:
            try:
                # Fetches the url for guitar tab.
                tab.fetch_by_track(track_name, artist_name)
                track.find_track(track_name, artist_name)
                if tab.tab_url is None:
                    st.error('Connection to Songsterr failed.')
                else:
                    confirmed_track_name = track.track_data['tracks']['items'][0]['name']
                    confirmed_artist_name = track.track_data['tracks']['items'][0]['artists'][0]['name']
                    st.info(f'Search Result: {confirmed_track_name} by {confirmed_artist_name}')
                    redirect, share, fav = st.columns(3, gap='medium')
                    with redirect:
                        st.link_button('Redirect to Interactive Tab', tab.tab_url)
                    with share:
                        st.link_button('Share to Facebook', f'https://www.facebook.com/sharer/sharer.php?u={tab.tab_url}')
                    with fav:
                        if st.button('Save Track to My Favourite'):
                            save_to_file(f'\n{confirmed_track_name}, {confirmed_artist_name}')
                            st.info('Successfully saved.')

                # Gathers and parses album related information
                track.extract_album_info(track_name, artist_name)

                # Gathers and parses artist related information
                track.extract_artist_info(artist_name)
                track.extract_related_artist(artist_name)
                track.extract_top_tracks(artist_name)

                # Gathers track audio feature
                track.find_track_audio_feature(track_name, artist_name)

                # Initiates two tabs, one for displaying album information, another for displaying artist information
                album, artist, track_audio, = st.tabs(['Album Information', 'Artist Information', 'Track Audio Features'])

                album_info = track.album_info
                artist_info = track.artist_info
                list_of_related_artists = track.list_of_related_artists
                dict_of_top_tracks = track.dict_of_top_tracks
                audio_features = track.track_audio_feature

                # This tab displays album information
                with album:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(album_info["image"])
                    with col2:
                        st.markdown(f'- Name: {album_info["name"]}')
                        st.markdown(f'- Artist: {album_info["artist"]}')
                        st.markdown(f'- Popularity: {convert_popularity(album_info["popularity"])}')
                        st.markdown(f'- Release date: {album_info["release_date"]}')
                        st.markdown(f'- Label: {album_info["label"]}')
                        st.markdown(f'- Number of tracks: {album_info["num_of_tracks"]}')
                        expander = st.expander('__List of Tracks__')
                        with expander:
                            for track in album_info['tracks']:
                                st.markdown(f'{track}')
                        st.link_button('Redirect to Spotify Page', f'{album_info["spotify_url"]}')

                # This tab displays artist information
                with artist:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(artist_info['image'])
                    with col2:
                        st.markdown(f'- Name: {artist_info["name"]}')
                        st.markdown(f'- Popularity: {convert_popularity(artist_info["popularity"])}')
                        expander_genre = st.expander('__Genres__')
                        with expander_genre:
                            for genre in artist_info['genre']:
                                st.markdown(f'{genre.capitalize()}')
                        expander_top_tracks = st.expander('__Top Tracks__')
                        with expander_top_tracks:
                            df = pd.DataFrame(list(dict_of_top_tracks.items()), columns=['Track', 'Popularity'])
                            st.dataframe(df, hide_index=True, width=WIDTH)
                        expander_related = st.expander('__Related Artists__')
                        with expander_related:
                            for artist in list_of_related_artists:
                                st.markdown(f'{artist}')
                        st.link_button('Redirect to Spotify Profile', f'{artist_info["spotify_url"]}')

                # This tab displays track audio features
                with track_audio:
                    dict_audio_feature = {}
                    key = convert_key(audio_features['key'])
                    mode = convert_mode(audio_features['mode'])
                    bpm = round(audio_features['tempo'])
                    time_sig = convert_time_signature(audio_features['time_signature'])

                    dict_audio_feature['Key'] = key
                    dict_audio_feature['Mode'] = mode
                    dict_audio_feature['BPM'] = bpm
                    dict_audio_feature['Time Signature'] = time_sig
                    df = pd.DataFrame(list(dict_audio_feature.items()), columns=['Feature', 'Value'])
                    st.dataframe(df, hide_index=True, width=WIDTH)

            except requests.exceptions.ConnectionError as ex:
                st.error(ex)
            except ValueError as ex:
                # This validates the input.
                st.error(ex)

    # Function chosen is to search for artist
    elif response == options[1]:
        st.text_input('Enter name of the track', disabled=True, placeholder='Track name is not required for this search type.')
        artist_name = st.text_input('Enter name of the artist')

        if artist_name:
            try:
                # Gathers list of tabs available on Songsterr
                tab.fetch_by_artist(artist_name)
                tab.filter_artist_data()
                tab.extract_artist_tracks()

                # Gathers and parses artist related information
                track.extract_artist_info(artist_name)
                track.extract_related_artist(artist_name)
                track.extract_top_tracks(artist_name)

                # Initiates two tabs, one for displaying list of available tabs, another for displaying artist information
                artist, tabs = st.tabs(['Artist Information', 'List of Available Guitar Tabs on Songsterr For This Artist'])

                tab_list = tab.artist_tracks
                artist_info = track.artist_info
                list_of_related_artists = track.list_of_related_artists
                dict_of_top_tracks = track.dict_of_top_tracks

                # This tab displays artist information
                with artist:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(artist_info['image'])
                    with col2:
                        st.markdown(f'- Name: {artist_info["name"]}')
                        st.markdown(f'- Popularity: {convert_popularity(artist_info["popularity"])}')
                        expander_genre = st.expander('__Genres__')
                        with expander_genre:
                            for genre in artist_info['genre']:
                                st.markdown(f'{genre.capitalize()}')
                        expander_top_tracks = st.expander('__Top Tracks__')
                        with expander_top_tracks:
                            df = pd.DataFrame(list(dict_of_top_tracks.items()), columns=['Track', 'Popularity'])
                            st.dataframe(df, hide_index=True, width=WIDTH)
                        expander_related = st.expander('__Related Artists__')
                        with expander_related:
                            for artist in list_of_related_artists:
                                st.markdown(f'{artist}')
                        st.link_button('Redirect to Spotify Profile', f'{artist_info["spotify_url"]}')

                # This tab displays list of available tabs
                with tabs:
                    col1, col2 = st.columns(2)
                    for tab1, tab2 in zip(tab_list[:len(tab_list) // 2], tab_list[len(tab_list) // 2:]):
                        with col1:
                            st.markdown(f'- {tab1}')
                        with col2:
                            st.markdown(f'- {tab2}')
                        
            except requests.exceptions.ConnectionError as ex:
                st.error(ex)
            except ValueError as ex:
                # This validates the input.
                st.error(ex)

    # Displays and edits the 'My Favourite' List
    else:
        # Initiate a file to save the list, if it doesn't exist in the current directory
        cwd = os.getcwd()
        file_path = os.path.join(cwd, FILENAME)
        if not os.path.isfile(file_path):
            with open(FILENAME, 'w') as file:
                file.write('')
            st.dataframe(pd.DataFrame(columns=['Track', 'Artist', 'Hour Practiced']), hide_index=True, width=WIDTH)

        # If it exists, then checks if it's non-empty. If it's not, read from it
        else:
            with open(FILENAME, 'r') as file:
                file.seek(0)
                if file.read() != '':
                    df = pd.read_csv(FILENAME, header=None, names=['Track', 'Artist'])
                    df['Hours Practiced'] = [0 for _ in range(len(df))]
                    edited_df = st.data_editor(df, hide_index=True, width=WIDTH, disabled=('Track', 'Artist'))

                    # Below is for manipulating the My Favourite list
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander('Remove a Track'):
                            track_to_remove = st.text_input('Please enter the name of the track to remove.')
                            if track_to_remove:
                                capitalized_track_to_remove = ' '.join([word.capitalize() for word in track_to_remove.split(" ")])
                                if capitalized_track_to_remove in list(df['Track']):
                                    remove_from_file(capitalized_track_to_remove)
                                    st.write('Successfully removed.')
                                    st.rerun()
                                else:
                                    st.error('Track cannot be found in My Favourite.')
                    with col2:
                        if st.button('Clear the List'): 
                            clear_file()
                            st.rerun()

                    # Plot a bar chart indicating whether the practice time has reached targeted practice time
                    x = list(edited_df['Track'])
                    y = list(edited_df['Hours Practiced'])
                    st.info('Enter hours practiced for each track in the list to see progress.')
                    if not any(y) == 0:
                        target_time = st.text_input('Set targeted practice hours')
                        if target_time:
                            target_time = int(target_time)
                        plt.bar(x, y, color='salmon')
                        plt.ylabel('Hours Practiced')
                        if target_time:
                            plt.axhline(y=target_time, color='grey', linestyle='--', label='Targeted Practice Time')
                        plt.ylim(0, 50)
                        plt.legend()
                        st.pyplot(plt)

                else:
                    st.dataframe(pd.DataFrame(columns=['Track', 'Artist', 'Hour Practiced']), hide_index=True, width=WIDTH)

if __name__ == '__main__':
    main()
