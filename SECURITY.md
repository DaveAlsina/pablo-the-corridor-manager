# Security Policy

## Supported Versions

| Version | Status |
|---|---|
| 1.0.x | ✅ Supported |
| 0.1.x | ❌ No longer supported |

---

## Reporting a Vulnerability

If you discover a security vulnerability, **do not open a public issue**. Instead:

1. Email the maintainer directly (see GitHub profile)
2. Describe the vulnerability and steps to reproduce
3. We aim to respond within 72 hours

---

## Security Considerations for Operators

### Bot Token
- Keep `TELEGRAM_BOT_TOKEN` secret — anyone with it controls your bot
- Never commit `.env` to git (`.gitignore` already excludes it)
- Rotate the token via @BotFather if it's ever exposed

### Database
- PostgreSQL is not exposed publicly (port 5432 is local-only in the default docker-compose)
- Use a strong, unique `POSTGRES_PASSWORD`
- Consider periodic backups in case of disk failure

### Server
- Keep Docker and the OS updated
- Restrict SSH access (use keys, not passwords)
- The bot does not need inbound open ports — it uses Telegram long-polling

### Telegram Group
- Only add trusted people to your corridor group
- The bot respects Telegram's privacy settings — group privacy mode should be OFF for the bot to work (see GET_STARTED.md)

---

## What the Bot Stores

The bot only stores what's needed to function:
- Telegram user ID, first name, @username
- Task completion records
- Opt-out reasons

It does not store message content, location, or any other personal data.
