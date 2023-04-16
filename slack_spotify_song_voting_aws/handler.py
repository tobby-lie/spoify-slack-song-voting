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

# process_before_response must be True when running on FaaS
app = App(
    process_before_response=True,
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

dynamodb = boto3.client("dynamodb")


def send_spotify_poll_message(channel: str, songs: List[str], client, logger):
    """Method that sends a poll message for spotify-song-vote slash command"""
    logger.info(f"Sending spotify poll message to slack channel: {channel}")
    slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
        SlackSpotifyPlaylistSongPoll(channel=channel, songs=songs)
    client.chat_postMessage(**slack_spotify_playlist_song_poll.message)
    sqs_client = boto3.client("sqs")
    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps({"note_id": str(note.id)}),
    )
    return


@app.command("/spotify-song-vote")
def respond_to_slack_within_3_seconds(ack, context, client, logger):
    """TODO"""
    logger.info("Handling request for /spotify-song-vote slash command")
    ack()
    spotify_playlist: SpotifyPlaylist = SpotifyPlaylist(
        spotify_username=SPOTIFY_USERNAME,
        spotify_playlist_name=SPOTIFY_PLAYLIST_NAME
    )
    # TODO: Randomize the selection of NUM_SONGS songs from playlist
    send_spotify_poll_message(
        channel=context.channel_id,
        songs=spotify_playlist.spotify_playlist_track_names[:NUM_SONGS],
        client=client,
        logger=logger
    )
    return


def reaction_event_update(
    event,
    table_name: str = "spotify-slack-bot-table-poc",
    reaction_removed: bool = False
) -> Dict[str, Any]:
    """TODO"""
    count_increment: str = "1" if not reaction_removed else "-1"
    add_update_expression: str = \
        " ".join([f"#{i}_count :{i}_count_val," for i in NUM_SONGS_RANGE])[:-1]
    return {
        "TableName": table_name,
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
def handle_reaction_added_event(client, event, context, logger, body):
    logger.info(event)
    # if event["reaction"] == "lock":
    messages = client.conversations_history(channel=context.channel_id)["messages"]
    matching_message = \
        next((message for message in messages if result["ts"] == event["item"]["ts"]))
    dynamodb.update_item(**reaction_event_update(event=event))
    client.chat_postMessage(channel=context.channel_id, text=f"{results['messages']=}{event['item']['ts']=}")


@app.event("reaction_removed")
def handle_reaction_removed_event(client, event, context, logger):
    logger.info(event)
    dynamodb.update_item(**reaction_event_update(event=event, reaction_removed=True))
    client.chat_postMessage(channel=context.channel_id, text=f"{event}")


SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
