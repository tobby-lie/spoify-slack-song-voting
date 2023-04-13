import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import slack
from dotenv import load_dotenv
from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter

from spotify_slack_song_voting.slack_spotify_playlist_song_poll import (
    SlackSpotifyPlaylistSongPoll,
)
from spotify_slack_song_voting.spotify_playlist import SpotifyPlaylist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize Flask app
app = Flask(__name__)

# Bind slack event addapter to Flask app
slack_event_adapter = SlackEventAdapter(
    os.environ["SIGNING_SECRET"], "/slack/events", app
)

# Initialize slack client
client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

# TODO: place this state in a database eventually so shut down of server does not lose
# state
TIMESTAMP_TO_SONG_POLLS: Dict[str, SlackSpotifyPlaylistSongPoll] = {}
NUM_SONGS: int = 5


def send_spotify_poll_message(channel: str, songs: List[str]):
    """Method that sends a poll message for spotify-song-vote slash command"""
    logger.info(f"Sending spotify poll message to slack channel: {channel}")
    slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
        SlackSpotifyPlaylistSongPoll(channel=channel, songs=songs)
    post_message_response: slack.web.slack_response.SlackResponse = \
        client.chat_postMessage(**slack_spotify_playlist_song_poll.message)
    
    TIMESTAMP_TO_SONG_POLLS[post_message_response["ts"]] = \
        slack_spotify_playlist_song_poll
    return


@app.route("/spotify-song-vote", methods=["POST"])
def spotify_song_vote() -> Tuple[Response, int]:
    """
    POST route for /spotify-song-vote slash command
    
    Returns:
        Tuple of flask Response and reponse code of 200
    """
    logger.info("Handling POST request for /spotify-song-vote slash command")
    spotify_playlist: SpotifyPlaylist = SpotifyPlaylist(
        spotify_username="s99lhk0fsvezlwg66z02fz9me",
        spotify_playlist_name="spotify-slack-integration"
    )
    # TODO: Randomize the selection of NUM_SONGS songs from playlist
    send_spotify_poll_message(
        channel=request.form.get("channel_id"),
        songs=spotify_playlist.spotify_playlist_track_names[:NUM_SONGS]
    )
    return Response(), 200


# TODO: filter check for max count emoji for just numerical emojis, currently random
# emojis can cause the voting count logic to not work such as in the case of a random
# emoji count being the same as the max numerical emoji count
@slack_event_adapter.on("reaction_added")
def reaction(payload):
    event = payload.get("event", {})
    channel_id = event.get("item", {}).get("channel")
    timestamp = event.get("item", {}).get("ts")
    timestamp_key = str(timestamp)
    reactions_get_data = client.reactions_get(channel=channel_id, timestamp=timestamp)

    # If vote is completed, check for winning song
    if (
        "lock" in [
            reaction["name"]
            for reaction in reactions_get_data.get('message').get('reactions')
        ] and not TIMESTAMP_TO_SONG_POLLS[timestamp_key].completed
    ):
        logger.info("Poll has been closed, finding top voted song name")
        # Get reaction emoji that was used the most in poll
        max_count_reaction_emoji = max(
            reactions_get_data.get('message').get('reactions'),
            key=lambda item: item['count']
        )["name"]

        # Get song related to most used emoji
        winning_song = TIMESTAMP_TO_SONG_POLLS[
            timestamp_key
        ].emoji_names_to_songs.get(max_count_reaction_emoji, "")

        # Set winning song and completion flag for poll with timestamp_key
        TIMESTAMP_TO_SONG_POLLS[timestamp_key].winning_song = winning_song
        TIMESTAMP_TO_SONG_POLLS[timestamp_key].completed = True

        client.chat_update(
            **TIMESTAMP_TO_SONG_POLLS[timestamp_key].message,
            ts=timestamp
        )


if __name__ == "__main__":
    app.run(debug=True)
