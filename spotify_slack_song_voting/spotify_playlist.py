"""
Module to generate and return playlist tracks from a specified Spotify username and
playlist name
"""
import logging

# from pathlib import Path
from typing import List, Optional

import spotipy

# from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# env_path = Path(".") / ".env"
# load_dotenv(dotenv_path=env_path)

SPOTIPY_CLIENT_ID: str = "d54f5cb052d0435ca4bac61385aa8805"
SPOTIPY_CLIENT_SECRET: str = "8c3c954f6ace4d5bab3944fbd673cc1c"
SLACK_TOKEN: str = "xoxb-4849396745840-4822786434229-UiarvtSy4Ug4KuPIMmrw3nIb"
SIGNING_SECRET: str = "74632507c18cf19616123961e7ff920a"


class SpotifyPlaylist:
    """Class responsible for getting a Spotify users' tracks from a specific playlist"""

    def __init__(self, spotify_username: str, spotify_playlist_name: str) -> None:
        """Initialize spotify client, username, and playlist name"""
        # NOTE: Must ensure that SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are set as
        # environment variables to call SpotifyClientCredentials with no params
        # For example:
        #   > export SPOTIPY_CLIENT_ID = <spotify api client id>
        #   > export SPOTIPY_CLIENT_SECRET = <spotify api client secret>
        self.__spotify_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
        self.spotify_username: str = spotify_username
        self.spotify_playlist_name: str = spotify_playlist_name
        self._spotify_playlist_track_names: Optional[List[str]] = None

    def __repr__(self) -> str:
        """Returns string representation of class"""
        return (
            f"SpofiyPlaylist(spofity_username={self.spotify_username}"
            f", spotify_playlist_name={self.spotify_playlist_name}"
            f", spotify_playlist_tracknames={self.spotify_playlist_track_names})"
        )

    @property
    def spotify_playlist_track_names(self) -> List[str]:
        """Return playlist track names given a username and playlist"""
        logger.info(
            f"Obtaining track names from playlist: {self.spotify_playlist_name}"
        )
        if self._spotify_playlist_track_names is None:
            user_playlists_data = self.__spotify_client.user_playlists(
                self.spotify_username
            )
            desired_playlist_data = next(
                playlist
                for playlist in user_playlists_data["items"]
                if playlist["name"] == self.spotify_playlist_name
            )
            self._spotify_playlist_track_names = [
                track["track"]["name"]
                for track in self.__spotify_client.playlist(
                    desired_playlist_data["id"],
                    fields="tracks"
                )["tracks"]["items"]
            ]
        return self._spotify_playlist_track_names


if __name__ == '__main__':
    spotify_playlist = SpotifyPlaylist(
        spotify_username="s99lhk0fsvezlwg66z02fz9me",
        spotify_playlist_name="spotify-slack-integration"
    )
    logger.info(f"results: {spotify_playlist}")
