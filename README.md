### Milestone 1 Design Document
##### Jialu Bi

#### Latest Update:
The search function won't work any more because Songsterr terminated their support for this API.
I've uploaded it anyway to archive the code for this project.
There's a screencast which shows how this project used to work, when Songsterr API was still supported.

1. __Project summary__
   The web application serves a similar job to a search engine. Depending on the input, it'll find either a guitar tab or an artist's related information. There are two search types of this web application:
   I. __Search by track name__
      This search type is programmed for users who want to search for the guitar tab of a specific track. If the user chooses this search type, they'll need to provide both the name of the track and the name of the artist. The latter is required because lots of tracks can have redundant names. For example, both the band _The Cure_ and the singer _Adele_ have a track called _Lovesong_. The search results would contain a button redirecting to the interactive tab, as well as information for the artist, the album that the track belongs to, and the track's audio features. If the combination of track name and artist name cannot be found, user will be prompted with an error message.
   II. __Search by artist name__
      This search type is programmed for users who just want to search for artist information. The only input would be the name of the artist. The search result would be a list of the artist's available guitar tabs on Songsterr, as well as some basic information about the artist, including the image, the genres, etc. If the artist cannot be found, user will be prompted with an error message.
   I decided to put the choice of two different search types in the side bar, so that the user can switch between the two within one page, and the displayed content on the page will change accordingly. Therefore, there'll only be one page (main) for this web application. In my opinion, this looks clearer and is more intuitive.

2. __Description of the REST APIs__
   I. __Spotify API__
      url and documentation (same page):
      https://developer.spotify.com/documentation/web-api
      Description:
      I'll fetch artist data and album data from this API. I'll then use the data to display information about the artist and/or the album, including the name, the image, the genres, the popularity, the release date, etc.
      Endpoints:
      `/v1/search` - Finds the best-matched result for the given string. Could be used to search for track, artist, etc.
      `/v1/album` - Returns the album data given the id of the album.
      `/v1/artists` - Returns the artist data given the id of the artist.
      `/v1/audio-features` - Returns the audio features of a track given the id of the track.

   II. __Songsterr API__
      url and documentation (no longer available):
      https://www.songsterr.com/a/wa/api/
      Description:
      The documentation is no longer available after they did a complete re-design of their web page, but the API itself still works to some extent (it does have some weird behaviors I have to overcome), and there are tutorials available. I'll fetch guitar tab url and data from this API. I'll then display either the url or the list of available guitar tabs.
      Endpoints:
      `/a/wa/bestMatchForQueryString` - Finds the best-matched tab for the given string.
      `/a/ra/songs/byartists.json` - Finds the best-matched artist for the given string.
      
3. __List of features__
   I. __Search for guitar tab or artist information__
      Description:
      User can search for either a guitar tab or information of an artist. For the former, the search results will be a button redirecting to the guitar tab on Songsterr. For the latter, the search results will list the available tabs on Songsterr for that artist.
      Model:
      `Tab`
      REST API endpoint:
      For guitar tab: `/a/wa/bestMatchForQueryString` (Songsterr)
      For artist: `/a/ra/songs/byartists.json` (Songsterr)
      Pages:
      Main
   II. __Share the tab to Facebook__
      Description:
      User can share the guitar tab on Facebook upon clicking the 'Share to Facebook' button.
      Model:
      `Tab`
      REST API endpoint:
      N/A
      Pages:
      Main
   III. __Display extra information__
      Description:
      The search result will include extra information. If the user searched for a guitar tab, information about the artist, the album it belongs to and audio features of the track will also be displayed, which includes the image for album cover, the release date, the genres, etc. If the user searched for an artist, information about the artist will also be displayed.
      Model:
      `Track`
      REST API endpoint:
      For artist information: `/v1/search` (Spotify)
      For album information: `/v1/albums` (Spotify)
      For artist information: `/v1/artists` (Spotify)
      For audio features: `/v1/audio-features` (Spotify)
      Pages:
      Main
   IV. __Save tabs to a 'My Favourite' list__
      Description:
      Saves the tab to a 'My Favourite' list, so that the user could practice or refer to it later. User could also record their progress of practice on certain tracks by entering 'Hours Practiced' for each track in the displayed DataFrame. If this column is filled in, a bar chart will be displayed, where the height of the bar is the hours practiced, and the bar label is the name of the track.

4. __References__
   I. Tutorials:
      Getting Spotify API access token:
      https://www.youtube.com/watch?v=WAmEZBEeNmg
      Using Songsterr APIL
      https://publicapis.io/songsterr-music-api
   II. External ibraries:
      requests:
      https://requests.readthedocs.io
      pytest:
      https://docs.pytest.org/en/7.1.x/contents.html
      streamlit:
      https://docs.streamlit.io

5. __Code highlights__
   The pieces of code I'm proud of is the error handling part inside the `find_track()`, `find_artist()` and other fetching methods in `Track` class.
   ```python
   def find_track(self, track, artist):
   ...
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
   ```
   The `/v1/search` of Spotify API will try to return a best match for the input. If there's really nothing marginally similar to the input, it'll return an empty list. To ensure accurate search result, I introduced the Levenshtein Distance from Python's standard library difflib. It'll compare the two strings based on Levenshtein Distance, and return a similarity score between 0 and 1, with 1 referring to two strings being identical. I then set a threshold for this similarity score to ensure that the search result is indeed what the user is looking for, with some degree of typo tolerance. I searched quite a few of my favourite tracks and artists, and it works fine for the most part, which gives me a sense of accomplishment.

6. __Next steps__
   I. Runtime:
      I'm not satisfied with the runtime of my web application. Each time I interact with the application, the page will rerun, which takes quite some time. More importantly, I made probably too many calls to Spotify API when gathering data, which significantly slows down the application. If I had extra time, I'll definetely put the priority on optimizing runtime.
   II. More robust search:
      There's a tradeoff between accurate result and easy input. I set a high level of similarity score to ensure the results are accurate, but the user will have to provide a almost correct input. I'd like to work on this part too, see if I could make it easier for users to provided input, without losing accuracy of search results.

7. __Reflection__
   The most challenging part is definetely configuring the search function, so that it not only returns accurate results, but also prompts the user with error messages when no match to their input can be found. I must be highly creative to cover as many cases as possible. What's especially difficult to code is input validation. I need to be extremely thoughtful and careful with the work flow, so that I raise an error under the correct scenario, inside the correct method/function, and in the correct part of the work flow. Then, I need to be cautious about where I should catch that error in the main function and how. It takes me numerous trials and errors to achieve that. The different behaviours of the two APIs when invalid inputs are provided also increase the difficulty significantly.
