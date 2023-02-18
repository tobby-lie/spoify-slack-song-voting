FROM manifoldai/orbyter-ml-dev:4.1
WORKDIR /build/
COPY docker/requirements.txt /build/requirements.txt
RUN pip install -r requirements.txt

COPY spotify_slack_song_voting/ /mnt/spotify_slack_song_voting/

# Launch
WORKDIR /mnt/