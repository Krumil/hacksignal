# Security Setup Guide

## 🔐 Environment Variables Setup

This application requires sensitive credentials that should **NEVER** be committed to git. All sensitive configuration is now loaded exclusively from environment variables.

### 1. Create your local config file

```bash
# Copy the template to create your local config
cp backend/config.template.json backend/config.json
```

_Note: The config.json file no longer contains any sensitive data - all Telegram credentials are loaded from environment variables._

### 2. Set up environment variables

**Option A: Using .env file (recommended for development)**

```bash
# Copy the example file
cp env.example .env

# Edit .env and add your actual tokens
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHANNEL_ID=your_actual_channel_id_here

# Optional: Customize telegram settings
TELEGRAM_ENABLED=true
TELEGRAM_MAX_TWEETS_TO_SEND=15
TELEGRAM_MIN_SCORE_TO_SEND=0.3
```

**Option B: Using system environment variables**

```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="your_actual_bot_token_here"
$env:TELEGRAM_CHANNEL_ID="your_actual_channel_id_here"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="your_actual_bot_token_here"
export TELEGRAM_CHANNEL_ID="your_actual_channel_id_here"
```

### 3. Install dependencies (for .env file support)

```bash
cd backend
pip install -r requirements.txt
```

### 4. Get your Telegram credentials

1. **Bot Token**: Message @BotFather on Telegram

    - Send `/newbot` or use existing bot
    - Get your bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Channel ID**:
    - Add your bot to your channel as admin
    - Use a tool like @userinfobot to get channel ID
    - Format: `-1001234567890` (negative number for channels)

## ⚠️ Security Warnings

-   **NEVER** commit `.env` files with real tokens
-   **NO sensitive data** is stored in config.json anymore
-   **ALWAYS** use environment variables for credentials
-   **IMMEDIATELY REVOKE** any tokens that have been exposed
-   **REGULARLY ROTATE** your bot tokens as a security practice

## 🚨 Token Exposure Response

If you accidentally expose a token:

1. **Immediately revoke** the token via @BotFather
2. **Generate a new token**
3. **Update your environment variables**
4. **Clean git history** if the token was committed
5. **Force push** clean history to remote repositories

## 📝 Configuration Details

The application loads configuration in this priority order:

1. **Environment variables** (.env file or system env vars)
2. **config.json file** (for non-sensitive settings only)
3. **Default fallback values**

### Environment Variables Reference

| Variable                      | Required | Default | Description                         |
| ----------------------------- | -------- | ------- | ----------------------------------- |
| `TELEGRAM_BOT_TOKEN`          | **Yes**  | -       | Bot token from @BotFather           |
| `TELEGRAM_CHANNEL_ID`         | **Yes**  | -       | Channel ID (negative number)        |
| `TELEGRAM_ENABLED`            | No       | `true`  | Enable/disable telegram integration |
| `TELEGRAM_MAX_TWEETS_TO_SEND` | No       | `15`    | Max tweets per digest               |
| `TELEGRAM_MIN_SCORE_TO_SEND`  | No       | `0.3`   | Minimum score threshold             |

This ensures **NO sensitive data** is ever stored in config files.
