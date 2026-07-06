# text-to-image-bot

Telegram bot that turns text messages into 1200×1200 image cards. Cards are
designed as an HTML/CSS template (`card_template.html`) and rendered with
headless Chromium via Playwright.

Trailing `#hashtags` in a message are pulled out and drawn as a separate row;
hashtags inside the text are highlighted inline.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run playwright install chromium
```

Create a `.env`:

```
TELEGRAM_BOT_TOKEN=<your bot token>
IMAGE_DISPLAY_NAME="name"            # display name on the card
IMAGE_USERNAME="username"       # @handle on the card
AVATAR_PATH=avatar.png              # optional; defaults to avatar.jpg in repo root
```

The card identity always comes from these variables — the Telegram sender's
name is never used.

## Run

```sh
uv run bot.py
```

## Deploy

Deployed by `deploy.sh` (from namanvashistha.github.io), which clones this repo
on the server and runs `docker compose up -d --build`.

Secrets are not in git — one-time setup per server:

```sh
ssh <server>
mkdir -p ~/namanvashistha/text-to-image-bot   # if first deploy hasn't run yet
vim ~/namanvashistha/text-to-image-bot/.env   # TELEGRAM_BOT_TOKEN, IMAGE_DISPLAY_NAME, IMAGE_USERNAME
```

`git pull` never touches the untracked `.env`, so it survives redeploys. If the
directory is ever deleted and recloned, recreate it — the bot exits at startup
with a clear error when `TELEGRAM_BOT_TOKEN` is missing.
