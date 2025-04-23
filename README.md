# linkedin-discord-bot

[![ci](https://github.com/IAmSkweetis/linkedin-discord-bot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/IAmSkweetis/linkedin-discord-bot/actions/workflows/ci.yml)

A simple little discord bot that will search LinkedIn job postings daily at post them to discord.

## Installation

The package is on PyPi and can be installed with pip:

```bash
pip install linkedin-discord-bot
```

## Usage

Running the bot requires either a sqlite3 or postgres database to store state of jobs and queries. 

You will need the following environment variables set:

```bash
LINKEDIN_DISCORD_BOT_DISCORD_TOKEN
LINKEDIN_DISCORD_BOT_DISCORD_NOTIF_CHANNEL_ID
LINKEDIN_DISCORD_BOT_DB_CONNECTION_STRING
```

For a local dev flow, you can put these values in a dotenv file.

Then run the following command to start the bot. Note that the current implementation is running
in the foreground.

```bash
lidb bot start
```

### Alternative - Docker Compose

A docker compose file is provided in the repo. To use it, run:

```bash
docker compose build
docker compose create
docker compose start
```

The docker compose file will download a postgres container image and initiate a blank database using a local volume. It will also create an image based on the provided Dockerfile. The docker compose file references the image name. If you have built the container image using the Taskfile tasks, Docker compose will attempt to use that image before building a new one.

## Dev Setup

Requirements:
- [uv](https://docs.astral.sh/uv/)
- [Taskfile](https://taskfile.dev/)
- sqlite3

Clone the repo:
```bash
git clone git@github.com:IAmSkweetis/linkedin-discord-bot.git
```

Use uv to sync:
```bash
uv sync
```

Run the following scripts for local-dev setup:
```bash
# Install chromedriver
task setup:chromedriver

# Initialize the local db
task db:init

# Run any db migrations
task db:migrate
```
