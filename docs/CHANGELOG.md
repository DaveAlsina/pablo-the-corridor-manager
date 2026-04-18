# Changelog

All notable changes to Pablo the Corridor Manager are documented here.

---

## [1.0.0] — 2026-04-18 — First Release

### Highlights
Full automation added on top of the MVP: Pablito now manages the entire weekly cycle by himself — reminders, closing, and opening new weeks. No manual intervention needed.

### Added (since 0.1.0)
- ✅ **Scheduled reminders** — automatic messages sent Tuesday and Friday at 10:00 and 18:00 showing pending tasks, a progress bar, and who hasn't contributed yet
- ✅ **Automatic week closing** — every Sunday at 23:59, Pablito closes the current week and sends a summary to the group
- ✅ **Week summary messages** — contributors ranked by task count, gentle reminder for non-contributors
- ✅ **Automatic week generation** — immediately after closing, a new week is created and announced
- ✅ **Interactive inline menus** — full button-driven navigation replacing raw text commands
- ✅ **Private/group chat split** — sensitive actions (complete, amend, stats) are private; status/tasks are public
- ✅ **Task amendment** — undo a task completion (with group notification)
- ✅ **Corridor map** — `/map` shows a visual layout of task locations
- ✅ **Opt-out via menu** — in addition to command, opt-outs available through button interface
- ✅ **Handlers refactor** — `src/handlers/` module with `task_handlers.py`, `info_handlers.py`, `optout_handlers.py`
- ✅ **`src/menus.py`** — centralized menu/keyboard builder
- ✅ **`src/reminders.py`** — reminder scheduler
- ✅ **`src/week_manager.py`** — week rollover logic with `force_week_rollover()` utility

### Changed
- Week deadline moved from **Friday** to **Sunday** (23:59)
- Reminders now run **Tuesday + Friday** (not Wednesday + Friday)
- Project now managed with **uv** (not pip/requirements.txt)
- Python requirement bumped to **3.12+** (was 3.10+)
- README completely rewritten
- Architecture tree updated in PROJECT_STRUCTURE.md

### Known Gaps (planned for v1.1.0)
- Admin bot commands for manual week management not yet wired (backend logic exists in `week_manager.py::force_week_rollover`)
- No `/closeweek` or `/newweek` commands yet

---

## [0.1.0] — 2026-02-01 — Phase 1 MVP

### Added
- PostgreSQL database with Docker Compose
- SQLAlchemy ORM with 7 database models
- Core Telegram commands: `/start`, `/help`, `/status`, `/tasks`, `/complete`, `/ask`, `/mystats`
- 22 predefined task types (toilets, showers, kitchen, fridges, hallways, trash, wash room)
- Task opt-out system
- Database population script
- Setup verification script (`scripts/test_setup.py`)
- Makefile for common operations
- Initial documentation: README, QUICKSTART, DEPLOYMENT, PROJECT_STRUCTURE, GET_STARTED

---

## [Planned] — v1.1.0 — Admin Controls

- [ ] `/closeweek` command — manually close current week
- [ ] `/newweek` command — manually open a new week
- [ ] `/announce <msg>` — send group announcement from bot
- [ ] Admin role system

## [Planned] — v1.2.0 — Accountability

- [ ] Penalty calculation per missed task
- [ ] Photo evidence upload for task completion
- [ ] `/leaderboard` — weekly/monthly contributor ranking
- [ ] Backup/restore mechanism

## [Planned] — v2.0.0 — Analytics

- [ ] Grafana dashboard
- [ ] Most procrastinated tasks
- [ ] Popular completion days
- [ ] Individual contribution trends
- [ ] Export (CSV, JSON)

---

## Versioning

Follows [Semantic Versioning](https://semver.org/):
- **MAJOR** — incompatible database or API changes
- **MINOR** — new features, backwards compatible
- **PATCH** — bug fixes, backwards compatible

## Migration Notes

### 0.1.0 → 1.0.0
No schema changes. New code only (handlers refactor, reminders, week_manager).
- Run `uv sync` to update dependencies
- Restart the bot — automation starts automatically

### Fresh Install
```bash
uv run python scripts/populate_db.py
```
