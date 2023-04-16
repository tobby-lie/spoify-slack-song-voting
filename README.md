# spoify-slack-song-voting

## How to run the slack bot in it's current configuration:

### ngrok setup

1. Run `> brew install ngrok/ngrok/ngrok`
2. Create a free account at https://ngrok.com
3. In ngrok dashboard, go to Getting Started > Your Authtoken and copy your authtoken
4. Run `> ngrok config add-authtoken <token>`
5. Run `> ngrok http 5000` to expose your localhost server to a public facing url
6. NOTE: `Forwarding` address will be shown in CLI when command form step 5 has been executed. THIS ADDRESS CHANGES EVERY TIME YOU RE-RUN `ngrok http <port>`

### Spotify API setup

1. Create an account at https://developer.spotify.com/dashboard/login
2. Create an app
3. Navigate to your app and set `Client ID` as `SPOTIPY_CLIENT_ID` and `Client Secret` as `SPOTIPY_CLIENT_SECRET` in `.env` file

### Slack API Setup

1. Create an account at https://api.slack.com/
2. Create a new app `from scratch`
3. Navigate to `Settings > Basic Information > Building Apps for Slack > App features and functionality > Bots`
4. Click `Review Scopes to Add`
5. Add the following OAuth Scopes: `channels:history`, `chat:write`, `commands`, `im:write`,and `reaction:read`
6. Click `Install App to Workspace`
7. Copy `Bot User OAuth Token` and set as `SLACK_TOKEN` variable in `.env` file
8. Create the channel you want to use the bot in
9. In the newly created channel, go to `Integrations > Add an App` and add your new app
10. In `Settings > Basic Information`, copy `Signing Secret` and set as `SIGNING_SECRET` IN `.env` file
11. Back in the slack api dashboard, navigate to your app then `Features > Event Subscriptions`
12. Under `Enable Events > Request URL`, paste your `Forwarding` address in the ngrok CLI followed by `/slack/events`
13. Under Subscribe to bot events add the following bot user events: `message.channels`, `reaction_added`
14. Now navigate to `Features > Slash Commands > Create New Command`
15. Input `/spotify-song-vote` for `Command`, the ngrok `Forwarding` address for `Request URL` followed by `/spotify-song-vote`

### Python code setup

1. Run `> python3 -m venv venv`
2. Run `> pip install .` at root director of the project
3. Run `> source venv/bin/activate`

### Running the bot server and slash command

1. Make sure you have followed along with `ngrok setup` section.
2. Run `> python spotify_slack_song_voting/slack_spotify_song_vote.py`
3. In slack channel, run `/spotify-song-vote`
4. Vote on the song you want by reacting with the corresponding emoji
5. Once finished voting, react with the :lock: emoji and the winning song will be outputted

## Current AWS Configuration

### AWS Resources utilized + purposes

1. AWS Lambdas
   1. `spotify-slack-bot-lambda-poc` is responsible for handling incoming requests from the Slack API such as events and slash commands. This Lambda is exposed as a function url so that it can accept incoming Slack requests.
   2. `spotify-slack-bot-put-survey-songs-lambda-poc` when a poll is initiated, the song titles for the vote are sent to an SQS queue so that they can be stored in the dynamodb table. This is decoupled as slash commands must complete in 3 seconds or less, or else a timeout error is returned. Writing to SQS takes less time than writing to DynamoDB which does take longer than 3 seconds. This Lambda is triggered by an SQS (will be described below).
2. SQS
   1. `spotify-slack-bot-sqs-poc` as mentioned, SQS is required so the process of storing song poll song titles is decoupled from request handling.
3. DynamoDB
   1. `spotify-slack-bot-table-poc` this table contains data for both song titles for a poll as well as counts for votes. The partitioning field is `message_id` which allows for handlers to keep track of which message they are manipulating.
4. ECR
   1. `spotify-slack-bot-image-poc` contains the Docker image that is executed by the `spotify-slack-bot-lambda-poc` Lambda.
   2. `spotify-slack-bot-put-survey-songs-image-poc` contains the Docker image that is executed by the `spotify-slack-bot-put-survey-songs-lambda-poc` Lambda.

### How to update Lambda handler code?

Currently, the process to update Lambda handler code is manual, the steps are listed below.

Before running any upload commands to ECR, the steps here must be followed: https://manifoldai.quip.com/aBc2AVahClny/Manifolds-AWS-SSO-sandbox-account-user-guide

After following the above steps, you must then run `aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <AWS account ID>.dkr.ecr.us-west-2.amazonaws.com`

Here are the steps to upload Docker images to the two Lambdas (Make sure you are in the root directory of the project):

1. spotify-slack-bot-lambda-poc

   1. Run `docker build -t spotify-slack-bot-image-poc -f slack_spotify_song_voting_aws/api_handler/Dockerfile .`
   2. Run `docker tag spotify-slack-bot-image-poc:latest 720068558948.dkr.ecr.us-west-2.amazonaws.com/spotify-slack-bot-image-poc:latest`
   3. Run `docker push 720068558948.dkr.ecr.us-west-2.amazonaws.com/spotify-slack-bot-image-poc:latest`
   4. Once pushed successfully, change the Docker image for the Lambda to point at the new `latest`

2. spotify-slack-bot-put-survey-songs-lambda-poc
   1. Run `docker build -t spotify-slack-bot-put-survey-songs-image-poc -f slack_spotify_song_voting_aws/sqs_handler/Dockerfile .`
   2. Run `docker tag spotify-slack-bot-put-survey-songs-image-poc:latest 720068558948.dkr.ecr.us-west-2.amazonaws.com/spotify-slack-bot-put-survey-songs-image-poc:latest`
   3. Run `docker push 720068558948.dkr.ecr.us-west-2.amazonaws.com/spotify-slack-bot-put-survey-songs-image-poc:latest`
   4. Once pushed successfully, change the Docker image for the Lambda to point at the new `latest`

### Slack API integration

Make sure slash command and event subscription request urls are both pointed at the `spotify-slack-bot-lambda-poc` function url.

### Future Work

1. Terraform the current AWS resources to document infrastructure as code (This ranges from resources all the way through to their IAM role policies.)
2. Create bash scripts to automate the pushing of Lambda handler ECR images
3. Implement code to delete old records in DynamoDB
4. Make SQS handler more robust to failures, perhaps include a deadletter queue
