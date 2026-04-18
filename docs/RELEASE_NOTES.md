# Release Notes — v1.0.0

**Release date:** April 18, 2026  
**Type:** First stable release

---

## What's in v1.0.0

This is the first release of Pablito as a fully autonomous corridor manager. It builds on the v0.1.0 MVP by adding full automation — the bot now runs the entire weekly cycle without any manual intervention.

### Automation

The three most important additions are:

1. **Scheduled reminders** — Pablito sends reminder messages to the group on Tuesday and Friday (twice each day) showing pending tasks, a progress bar, and who hasn't contributed yet. If all tasks are done, he celebrates instead.

2. **Automatic week closing** — Every Sunday at 23:59, the current week is closed. A summary is sent to the group ranking contributors and gently noting who missed the week.

3. **Automatic week generation** — Immediately after closing, a new week is created with fresh task instances and announced to the group.

### Interactive Menus

The bot now uses inline keyboard buttons for everything. Instead of typing commands, residents tap buttons to navigate category → task → confirm. This makes the bot approachable for everyone, not just people comfortable with chat commands.

### Private/Group Chat Separation

Sensitive actions (completing tasks, viewing personal stats) now happen in private chat. The group chat is for public status only. When someone tries a private action from the group, the bot sends a button that opens private chat directly.

### Refactored Architecture

The codebase was split into a proper handler module (`src/handlers/`) with separate files for task actions, info queries, and opt-outs. `src/menus.py` centralizes all keyboard builders. This makes the code maintainable as features are added.

---

## Breaking Changes from 0.1.0

**None** — the database schema is unchanged. A clean `uv sync` and restart is sufficient.

**Configuration change:** The deadline day moved from Friday to Sunday. If you had `WEEK_DEADLINE_DAY=friday` in your `.env`, update it to `sunday`.

---

## Known Limitations in This Release

- **No admin bot commands** — manual week management requires direct Python calls (see [ADMIN_GUIDE.md](ADMIN_GUIDE.md)). Admin commands (`/closeweek`, `/newweek`) are the first priority for v1.1.0.
- **No penalty enforcement** — the `penalties` table exists and the schema is ready, but no logic calculates or assigns penalties yet.
- **No photo evidence** — tasks are completed by tapping a button, not by uploading a photo. This keeps friction low but means no visual proof.
- **Server timezone** — reminder times are in server local time. If your server is UTC and you're in Amsterdam, adjust `REMINDER_TIMES` in `src/reminders.py`.

---

## Upgrading from 0.1.0

```bash
git pull origin main
uv sync
# Restart the bot
make start
```

No database migrations needed.

---

## What's Next

**v1.1.0** — Admin Commands
- `/closeweek` and `/newweek` bot commands
- Admin role system

**v1.2.0** — Accountability
- Penalty calculation
- Photo evidence
- Leaderboard

See [CHANGELOG.md](CHANGELOG.md) for the full roadmap.
