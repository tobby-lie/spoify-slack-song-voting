"""Handler for slack api requests"""
import json
import logging
import os
from typing import Any, Dict, List

import boto3
import slack
from num2words import num2words
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from spotify_slack_song_voting.slack_spotify_playlist_song_poll import (
    SlackSpotifyPlaylistSongPoll,
)
from spotify_slack_song_voting.spotify_playlist import SpotifyPlaylist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SLACK_BOT_TOKEN: str = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET: str = os.environ["SLACK_SIGNING_SECRET"]
SPOTIFY_USERNAME: str = os.environ["SPOTIFY_USERNAME"]
SPOTIFY_PLAYLIST_NAME: str = os.environ["SPOTIFY_PLAYLIST_NAME"]
SQS_QUEUE_URL: str = os.environ["SQS_QUEUE_URL"]

NUM_SONGS: int = int(os.environ["NUM_SONGS"])
NUM_SONGS_RANGE: range = range(1, NUM_SONGS + 1)

DYNAMODB_TABLE_NAME: str = os.environ["DYNAMODB_TABLE_NAME"]

# process_before_response must be True when running on FaaS
app = App(
    process_before_response=True,
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

DYNAMODB_CLIENT = boto3.client("dynamodb")


def send_spotify_poll_message(channel: str, songs: List[str], client, logger):
    """Method that sends a poll message for spotify-song-vote slash command"""
    logger.info(f"Sending spotify poll message to slack channel: {channel}")
    slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
        SlackSpotifyPlaylistSongPoll(channel=channel, songs=songs)
    post_message_response: slack.web.slack_response.SlackResponse = \
        client.chat_postMessage(**slack_spotify_playlist_song_poll.message)

    sqs_client = boto3.client("sqs")
    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        # TODO: Structure SQS payload better as message attributes
        MessageBody=json.dumps(
            {
                "message_id": post_message_response["ts"],
                **{
                    f"song_{i+1}": song
                    for i, song in enumerate(songs)
                }
            }
        ),
    )
    return


@app.command("/spotify-song-vote")
def respond_to_slack_within_3_seconds(ack, context, client, logger):
    """
    Handler for /spotify-song-vote slash command, songs to be displayed must be sorted

    Args:
        ack: Used to return acknowledgement to Slack servers
        context: context data associated with incoming request
        client: slack sdk web client instance
        logger: slack sdk logger instance
    """
    logger.info("Handling request for /spotify-song-vote slash command")
    ack()
    spotify_playlist: SpotifyPlaylist = SpotifyPlaylist(
        spotify_username=SPOTIFY_USERNAME,
        spotify_playlist_name=SPOTIFY_PLAYLIST_NAME
    )
    # TODO: Randomize the selection of NUM_SONGS songs from playlist
    send_spotify_poll_message(
        channel=context.channel_id,
        # songs must be sorted to ensure consistency with output and db
        songs=sorted(spotify_playlist.spotify_playlist_track_names[:NUM_SONGS]),
        client=client,
        logger=logger
    )
    return


def reaction_event_update(event, reaction_removed: bool = False) -> Dict[str, Any]:
    """
    Updates dynamodb variables containing counts for vote rankings

    Args:
        event: slack event payload
        reaction_removed: flag to indicate if we should iinrement or decrement counts
    """
    count_increment: str = "1" if not reaction_removed else "-1"
    add_update_expression: str = \
        " ".join([f"#{i}_count :{i}_count_val," for i in NUM_SONGS_RANGE])[:-1]
    return {
        "TableName": DYNAMODB_TABLE_NAME,
        "Key": {
            "message_id": {"N": event["item"]["ts"]},
        },
        "UpdateExpression": (
            f"""SET #channel_id = if_not_exists(#channel_id, :channel_id)
            ADD {add_update_expression}"""
        ),
        "ExpressionAttributeNames": {
            **{
                f"#{i}_count": f"{i}_count" for i in NUM_SONGS_RANGE
            },
            "#channel_id": "channel_id"
        },
        "ExpressionAttributeValues": {
            **{
                f":{i}_count_val": {
                    "N": count_increment if event["reaction"] == num2words(i) else "0"
                }
                for i in NUM_SONGS_RANGE
            },
            ":channel_id": {"S": event["item"]["channel"]}
        }
    }


@app.event("reaction_added")
def handle_reaction_added_event(client, event, context, logger):
    """
    Handler for reaction added event

    Args:
        client: slack sdk web client instance
        event: slack event payload
        contex: context data for incoming request
        logger: slack logger instance
    """
    logger.info("Handling reaction added event")
    if event["reaction"] == "lock":
        response_items: Dict[str, Any] = DYNAMODB_CLIENT.get_item(
            Key={
                "message_id": {"N": event["item"]["ts"]}
            },
            TableName=DYNAMODB_TABLE_NAME,
        )["Item"]

        counts_dict: Dict[str, Any] = {
            key: int(val["N"])
            for key, val in response_items.items() if "count" in key
        }
        songs_dict: Dict[str, Any] = {
            key: val
            for key, val in response_items.items() if "song" in key
        }
        max_count_key: str = next(
            key for key, val in counts_dict.items() if val == max(counts_dict.values())
        )
        # max_count_key takes on the form of "1_count": {"N": <song_count>} for example
        winning_song: str = next(
            val["S"]
            for key, val in songs_dict.items() if max_count_key.split("_")[0] in key
        )

        # SlackSpotifyPlaylistSongPoll instance for updating messageth winning song
        slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
            SlackSpotifyPlaylistSongPoll(
                channel=context.channel_id,
                # songs_dict items take on the form of "song_1": {"S": <song_name>}
                # for example
                songs=sorted([val["S"] for _, val in songs_dict.items()]),
            )
        slack_spotify_playlist_song_poll.winning_song = winning_song
        slack_spotify_playlist_song_poll.completed = True

        client.chat_update(
            **slack_spotify_playlist_song_poll.message,
            ts=event["item"]["ts"]
        )
    else:
        DYNAMODB_CLIENT.update_item(**reaction_event_update(event=event))


@app.event("reaction_removed")
def handle_reaction_removed_event(event, logger):
    """
    Handler for reaction removed event

    Args:
        event: slack event payload
        logger: slack logger instance
    """
    logger.info("Handling reaction removed event")
    DYNAMODB_CLIENT.update_item(
        **reaction_event_update(event=event, reaction_removed=True)
    )


SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


# TODO: Type hint context
def lambda_handler(event: Dict[str, Any], context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
