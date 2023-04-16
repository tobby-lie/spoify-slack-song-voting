# run from a directory above or use the script to build!
FROM public.ecr.aws/lambda/python:3.8

COPY slack_spotify_song_voting_aws/sqs_handler/handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "handler.lambda_handler" ]
