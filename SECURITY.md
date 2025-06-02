# Security Setup Guide

## 🔐 Environment Variables Setup

This application requires sensitive credentials that should **NEVER** be committed to git. Follow these steps to set up your environment securely:

### 1. Create your local config file

```bash
# Copy the template to create your local config
cp backend/config.template.json backend/config.json
```

### 2. Set up environment variables

**Option A: Using .env file (recommended for development)**

```bash
# Copy the example file
cp env.example .env

# Edit .env and add your actual tokens
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHANNEL_ID=your_actual_channel_id_here
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

### 3. Get your Telegram credentials

1. **Bot Token**: Message @BotFather on Telegram

    - Send `/newbot` or use existing bot
    - Get your bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Channel ID**:
    - Add your bot to your channel as admin
    - Use a tool like @userinfobot to get channel ID
    - Format: `-1001234567890` (negative number for channels)

## ⚠️ Security Warnings

-   **NEVER** commit `.env` files or `config.json` files with real tokens
-   **ALWAYS** use environment variables for sensitive data
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

1. Environment variables (highest priority)
2. `config.json` file values
3. Default fallback values

This ensures environment variables always override file-based configuration for sensitive data.
