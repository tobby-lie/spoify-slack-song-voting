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
