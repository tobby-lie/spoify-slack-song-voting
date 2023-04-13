"""Module for slack spotify playlist song poll slash command"""
import logging
from typing import Dict, List, Optional, Union

from num2words import num2words

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackSpotifyPlaylistSongPoll:
    """Class encapsulating slack spotify playlist poll"""

    """Class attributes for structure of markdown message for a poll"""
    start_text = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "So you're having trouble choosing a song :thinking_face:\n"
                "Vote for a song with the following emojis\n"
            )
        }
    }
    divider = {"type": "divider"}
    end_text = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "To close this vote, react with :lock:"
        }
    }

    def __init__(self, channel: str, songs: List[str]):
        """
        Initialize slack channel, songs list, winning song, completion flag, and
        properties
        """

        # Slack channel and songs list generated from a spotify playlist
        self.channel: str = channel
        self.songs: List[str] = songs

        # Winning song from poll and if poll has been completed flag
        self.winning_song: str = ""
        self.completed: bool = False

        # Correlate emojis to songs
        self._emoji_names_to_songs: Optional[Dict[str, str]] = None
        self._songs_listing: Optional[List[str]] = None

        # Message output initialization
        self._blocks: Optional[List[Dict[str, Union[str, Dict[str, str]]]]] = None
        self._message: Optional[Dict[str, str]] = None

    def __repr__(self) -> str:
        """Return string representation of class"""
        return (
            f"SlackSpotifyPlaylistSongPoll(channel={self.channel}, songs={self.songs}, "
            f"message={self.message})"
        )

    @property
    def emoji_names_to_songs(self) -> Dict[str, str]:
        """
        Dict with emoji names as keys and song names as values
        
        Example:
            {
                "one": "song one",
                "two": "song two"
            }
        
        Returns:
            emoji names to songs dict
        """
        logger.info("Getting emoji names to songs dict")
        if self._emoji_names_to_songs is None:
            self._emoji_names_to_songs = {
                f"{num2words(i+1)}": self.songs[i]
                for i in range(len(self.songs))
            }
        return self._emoji_names_to_songs

    @property
    def songs_listing(self) -> List[str]:
        """
        List of songs to be used in message markdown output
        
        Returns:
            List of strings of format '<emoji number> <song name>'
        """
        logger.info("Getting list of songs for markdown output")
        if self._songs_listing is None:
            self._songs_listing = [
                f":{num2words(i+1)}: {self.songs[i]}\n"
                for i in range(len(self.songs))
            ]
        return self._songs_listing

    @property
    def blocks(self) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        """
        Blocks to be used as output for the markdown message used by Slack

        Returns:
            List of various markdown blocks
        """
        logger.info("Getting blocks for markdown message")
        song_list_text = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (f"{''.join(self.songs_listing)}")
            }
        }
        return (
            [
                self.divider,
                self.start_text,
                self.divider,
                song_list_text,
                self.divider,
                self.end_text,
                self.divider,
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":mega: Winning song is: {self.winning_song}"
                    }
                }
            ] if self.winning_song else [
                self.divider,
                self.start_text,
                self.divider,
                song_list_text,
                self.divider,
                self.end_text,
                self.divider,
            ]
        )

    @property
    def message(self) -> Dict[str, str]:
        """
        Message to be used for messaging by slack bot

        Returns:
            Dict containing channel and message blocks
        """
        logger.info("Getting slack message")
        return {
            "channel": self.channel,
            "blocks": self.blocks
        }
