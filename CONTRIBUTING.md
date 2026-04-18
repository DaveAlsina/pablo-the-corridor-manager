# Contributing

Thanks for your interest in improving Pablito!

---

## Project Context

This is a small self-hosted Telegram bot for managing corridor cleaning tasks in a shared flat. The priority is simplicity, reliability, and being easy to run on a Raspberry Pi.

---

## How to Contribute

### Reporting Bugs

Open a GitHub issue using the **Bug Report** template. Include:
- What you did
- What you expected
- What actually happened
- Logs (from `journalctl -u pablito -n 50` or the terminal)
- Your setup (OS, Python version, Docker version)

### Suggesting Features

Open an issue using the **Feature Request** template. Check the roadmap in README.md first — your idea might already be planned.

### Submitting Code

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test manually with a real Telegram bot
5. Run `uv run python scripts/test_setup.py`
6. Commit: `git commit -m "feat: add /closeweek command"`
7. Push and open a Pull Request

---

## Development Setup

```bash
git clone https://github.com/your-username/pablo-the-corridor-manager
cd pablo-the-corridor-manager
cp .env.example .env
# Edit .env with a test bot token
docker-compose up -d
uv sync
make populate
make start
```

---

## Code Style

- Follow existing patterns — handlers go in `src/handlers/`, menus in `src/menus.py`
- Use `with get_db() as db:` for all database access
- Private-only actions must check `is_private_chat()` before proceeding
- Group notifications go through `notify_group_func` (passed from `bot.py`)
- Keep docstrings on all public functions
- No type: ignore comments without explanation

---

## Commit Message Format

```
type: short description

feat:    new feature
fix:     bug fix
docs:    documentation only
refactor: code change without behavior change
chore:   build / config / tooling
```

---

## What We're Looking For

High priority for contributions:
- Admin bot commands (`/closeweek`, `/newweek`)
- Timezone-aware scheduling
- Better error messages for end users

Not currently accepting:
- Multi-corridor support (architecture change too large for now)
- Alternative databases (PostgreSQL is the target)

---

## Questions

Open an issue or discuss in the Telegram group if you're a corridor resident.
