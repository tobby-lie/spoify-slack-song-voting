from setuptools import find_packages, setup

setup(
    name="spotify_slack_song_voting",
    author="Tobby Lie",
    author_email="tobbylie@gmail.com",
    description="Spotify slack voting integration",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "Flask",
        "num2words",
        "python-dotenv",
        "slackclient",
        "slackeventsapi",
        "spotipy",
    ],
    license="MIT License",
)
