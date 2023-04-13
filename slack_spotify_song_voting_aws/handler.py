import logging

import slack
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# process_before_response must be True when running on FaaS
app = App(
    process_before_response=True,
    token="xoxb-4849396745840-4822786434229-UiarvtSy4Ug4KuPIMmrw3nIb",
    signing_secret="74632507c18cf19616123961e7ff920a"
)


# # listener matcher to check if the reaction should be handled
# def target_reactions_only(event) -> bool:
#     return event.get("reaction") in ["eyes", "white_check_mark"]


# @app.event(event="reaction_added", matchers=[target_reactions_only])
# def handle_target_reactions(body, logger):
#     # do something meaningful here
#     logger.info(body)


# @app.event("app_mention")
# def handle_app_mentions(body, say, logger):
#     logger.info(body)
#     say("What's up?")


# listener matcher: async function that returns bool
# def is_eyes(event: dict) -> bool:
#     return event["reaction"] == "eyes"


# @app.event("reaction_added", matchers=[is_eyes])
# def handle_eyes_reactions_only(body, logger):
#     logger.info(body)


# # common utility example
# def is_target_reaction(reaction: str):
#     async def is_target(event) -> bool:
#         return event["reaction"] == reaction
#     return is_target


# @app.event(
#     event="reaction_added",
#     matchers=[is_target_reaction("white_check_mark")],
# )
# async def handle_white_check_mark_reactions_only(body, logger):
#     logger.info(body)

# @app.command("/hello-bolt-python-lambda")
# def respond_to_slack_within_3_seconds(ack, respond, command):
#     ack(command)
#     respond(f"{command['text']}")

@app.command("/hello-bolt-python-lambda")
def respond_to_slack_within_3_seconds(ack, respond, context, command):
    ack(command)
    respond(f"{context=}")


@app.event("reaction_added")
def handle_reaction_added_events(client, event, context, body, logger, message):
    logger.info(event)
    client.chat_postMessage(channel=context.channel_id, text=f"{event}")


# The echo command simply echoes on command
@app.command("/echo")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    logger.info(f"{command=}")
    ack()
    respond(f"{command['text']}")



# def send_spotify_poll_message(channel: str, songs: List[str]):
#     """Method that sends a poll message for spotify-song-vote slash command"""
#     logger.info(f"Sending spotify poll message to slack channel: {channel}")
#     slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
#         SlackSpotifyPlaylistSongPoll(channel=channel, songs=songs)
#     post_message_response: slack.web.slack_response.SlackResponse = \
#         client.chat_postMessage(**slack_spotify_playlist_song_poll.message)
    
#     TIMESTAMP_TO_SONG_POLLS[post_message_response["ts"]] = \
#         slack_spotify_playlist_song_poll
#     return


# @app.route("/spotify-song-vote", methods=["POST"])
# def spotify_song_vote() -> Tuple[Response, int]:
#     """
#     POST route for /spotify-song-vote slash command
    
#     Returns:
#         Tuple of flask Response and reponse code of 200
#     """
#     logger.info("Handling POST request for /spotify-song-vote slash command")
#     spotify_playlist: SpotifyPlaylist = SpotifyPlaylist(
#         spotify_username="s99lhk0fsvezlwg66z02fz9me",
#         spotify_playlist_name="spotify-slack-integration"
#     )
#     # TODO: Randomize the selection of NUM_SONGS songs from playlist
#     send_spotify_poll_message(
#         channel=request.form.get("channel_id"),
#         songs=spotify_playlist.spotify_playlist_track_names[:NUM_SONGS]
#     )
#     return Response(), 200


SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


# import logging
# import time

# from slack_bolt import App
# from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# # process_before_response must be True when running on FaaS
# app = App(
#     process_before_response=True,
#     token="xoxb-4849396745840-4822786434229-UiarvtSy4Ug4KuPIMmrw3nIb",
#     signing_secret="74632507c18cf19616123961e7ff920a"
# )


# @app.middleware  # or app.use(log_request)
# def log_request(logger, body, next):
#     logger.debug(body)
#     return next()


# command = "/hello-bolt-python-lambda"


# def respond_to_slack_within_3_seconds(body, ack):
#     if body.get("text") is None:
#         ack(f":x: Usage: {command} (description here)")
#     else:
#         title = body["text"]
#         ack(f"Accepted! (task: {title})")


# def process_request(respond, body):
#     time.sleep(5)
#     title = body["text"]
#     respond(f"Completed! (task: {title})")


# app.command(command)(ack=respond_to_slack_within_3_seconds, lazy=[process_request])

# SlackRequestHandler.clear_all_log_handlers()
# logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


# def handler(event, context):
#     slack_handler = SlackRequestHandler(app=app)
#     return slack_handler.handle(event, context)

################################

# import json
# import logging
# from typing import Dict

# from slack_bolt import App
# from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# from spotify_slack_song_voting.slack_spotify_playlist_song_poll import (
#     SlackSpotifyPlaylistSongPoll,
# )
# from spotify_slack_song_voting.spotify_playlist import SpotifyPlaylist

# # import slack

# # from flask import Flask, Response, request
# # from mangum import Mangum
# # from slackers.server import router
# # from slackeventsapi import SlackEventAdapter


# # from fastapi import FastAPI, Request


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # TODO make these env vars in aws lambda
# SPOTIPY_CLIENT_ID: str = "d54f5cb052d0435ca4bac61385aa8805"
# SPOTIPY_CLIENT_SECRET: str = "8c3c954f6ace4d5bab3944fbd673cc1c"
# SLACK_TOKEN: str = "xoxb-4849396745840-4822786434229-UiarvtSy4Ug4KuPIMmrw3nIb"
# SIGNING_SECRET: str = "74632507c18cf19616123961e7ff920a"

# app = App(process_before_response=True, token=SLACK_TOKEN)

# # Initialize Flask app
# # app = FastAPI()
# # app.include_router(router=router)

# # Bind slack event addapter to Flask app
# # slack_event_adapter = SlackEventAdapter(
# #     SIGNING_SECRET, "/slack/events", app
# # )

# # Initialize slack client
# # client = slack.WebClient(token=SLACK_TOKEN)

# # TODO: place this state in a database eventually so shut down of server does not lose
# # state
# TIMESTAMP_TO_SONG_POLLS: Dict[str, SlackSpotifyPlaylistSongPoll] = {}
# NUM_SONGS: int = 5


# def handler(event, _):
#     return {
#         "statusCode": 200,
#         "body": json.loads(event["body"])["challenge"]
#     }

# # handler = Mangum(app=app)


# # @app.get('/')
# # async def root():
# #     return {"message": "Slack Bot - API"}


# # def send_spotify_poll_message(channel: str, songs: List[str]):
# #     """Method that sends a poll message for spotify-song-vote slash command"""
# #     logger.info(f"Sending spotify poll message to slack channel: {channel}")
# #     slack_spotify_playlist_song_poll: SlackSpotifyPlaylistSongPoll = \
# #         SlackSpotifyPlaylistSongPoll(channel=channel, songs=songs)
# #     # post_message_response: slack.web.slack_response.SlackResponse = \
# #     #     client.chat_postMessage(**slack_spotify_playlist_song_poll.message)
# #     client.chat_postMessage(**slack_spotify_playlist_song_poll.message)

# #     # TIMESTAMP_TO_SONG_POLLS[post_message_response["ts"]] = \
# #     #     slack_spotify_playlist_song_poll
# #     return


# # @app.post("/spotify-song-vote")
# # async def spotify_song_vote(request: Request) -> Dict[str, str]:
# #     """
# #     POST route for /spotify-song-vote slash command

# #     Returns:
# #         Tuple of flask Response and reponse code of 200
# #     """
# #     logger.info("Handling POST request for /spotify-song-vote slash command")
# #     spotify_playlist: SpotifyPlaylist = SpotifyPlaylist(
# #         spotify_username="s99lhk0fsvezlwg66z02fz9me",
# #         spotify_playlist_name="spotify-slack-integration"
# #     )
# #     # TODO: Randomize the selection of NUM_SONGS songs from playlist
# #     form_data: Request = await request.form()
# #     send_spotify_poll_message(
# #         channel=form_data.get("channel_id"),
# #         songs=spotify_playlist.spotify_playlist_track_names[:NUM_SONGS]
# #     )
# #     return {"detail": "Successfully started spotify song vote poll"}


# ########################

# # # TODO: filter check for max count emoji for just numerical emojis, currently random
# # # emojis can cause the voting count logic to not work such as in the case of a random
# # # emoji count being the same as the max numerical emoji count
# # @slack_event_adapter.on("reaction_added")
# # def reaction(payload):
# #     event = payload.get("event", {})
# #     channel_id = event.get("item", {}).get("channel")
# #     timestamp = event.get("item", {}).get("ts")
# #     timestamp_key = str(timestamp)
# #     reactions_get_data = client.reactions_get(channel=channel_id, timestamp=timestamp)

# #     # If vote is completed, check for winning song
# #     if (
# #         "lock" in [
# #             reaction["name"]
# #             for reaction in reactions_get_data.get('message').get('reactions')
# #         ] and not TIMESTAMP_TO_SONG_POLLS[timestamp_key].completed
# #     ):
# #         logger.info("Poll has been closed, finding top voted song name")
# #         # Get reaction emoji that was used the most in poll
# #         max_count_reaction_emoji = max(
# #             reactions_get_data.get('message').get('reactions'),
# #             key=lambda item: item['count']
# #         )["name"]

# #         # Get song related to most used emoji
# #         winning_song = TIMESTAMP_TO_SONG_POLLS[
# #             timestamp_key
# #         ].emoji_names_to_songs.get(max_count_reaction_emoji, "")

# #         # Set winning song and completion flag for poll with timestamp_key
# #         TIMESTAMP_TO_SONG_POLLS[timestamp_key].winning_song = winning_song
# #         TIMESTAMP_TO_SONG_POLLS[timestamp_key].completed = True

# #         client.chat_update(
# #             **TIMESTAMP_TO_SONG_POLLS[timestamp_key].message,
# #             ts=timestamp
# #         )


# # if __name__ == "__main__":
# #     app.run(debug=True)
