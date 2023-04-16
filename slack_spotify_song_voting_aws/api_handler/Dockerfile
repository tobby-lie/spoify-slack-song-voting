# run from a directory above or use the script to build!
FROM public.ecr.aws/lambda/python:3.8

COPY slack_spotify_song_voting_aws/api_handler/requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

RUN mkdir -p ${LAMBDA_TASK_ROOT}/slack_spotify_song_voting/
COPY spotify_slack_song_voting/slack_spotify_playlist_song_poll.py \
    spotify_slack_song_voting/spotify_playlist.py \
    ${LAMBDA_TASK_ROOT}/spotify_slack_song_voting/

COPY slack_spotify_song_voting_aws/api_handler/handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "handler.lambda_handler" ]
