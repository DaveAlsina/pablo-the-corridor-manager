# Project Structure

## File Tree

```
pablo-the-corridor-manager/
│
├── 📋 Root
│   ├── README.md                  # Project overview & quick start
│   ├── CONTRIBUTING.md            # How to contribute
│   ├── SECURITY.md                # Security policy
│   ├── CODE_OF_CONDUCT.md         # Community guidelines
│   ├── LICENSE                    # MIT license
│   ├── Makefile                   # Common commands (make help)
│   ├── pyproject.toml             # Python project + dependencies (uv)
│   ├── uv.lock                    # Locked dependency versions
│   ├── .python-version            # Python version pin (3.12)
│   ├── .env.example               # Environment variable template
│   ├── docker-compose.yml         # PostgreSQL + pgAdmin containers
│   └── alembic.ini                # Database migration config
│
├── 🐍 src/                        # Application source
│   ├── __init__.py
│   ├── bot.py                     # ⭐ Entry point — CorridorBot class
│   ├── models.py                  # SQLAlchemy models (7 tables)
│   ├── database.py                # DB connection + session utilities
│   ├── config.py                  # Pydantic settings (loads .env)
│   ├── menus.py                   # Inline keyboard builders
│   ├── reminders.py               # Scheduled reminder jobs (Tue/Fri)
│   ├── week_manager.py            # Automatic week rollover (Sunday)
│   └── handlers/
│       ├── __init__.py            # Exports all handler functions
│       ├── task_handlers.py       # Complete / amend / ask flows
│       ├── info_handlers.py       # Status / stats / tasks / map
│       └── optout_handlers.py     # Opt-out command and flow
│
├── 🛠️ scripts/                    # Dev & maintenance scripts
│   ├── __init__.py
│   ├── populate_db.py             # Seed 22 task types + test users
│   ├── reset_db.py                # Drop all tables (⚠️ destructive)
│   └── test_setup.py              # Verify installation health
│
├── 🗄️ alembic/                    # Database migrations
│   ├── env.py                     # Alembic runtime environment
│   ├── script.py.mako             # Migration file template
│   └── versions/                  # Migration files (auto-generated)
│
├── 🖼️ media/
│   └── corridor-overview.jpg      # Corridor map image (used by /map)
│
└── 📚 docs/
    ├── pablito.png                # Bot avatar / mascot
    ├── QUICKSTART.md              # 5-minute setup
    ├── GET_STARTED.md             # Detailed first-time setup
    ├── COMMANDS.md                # Full command & button reference
    ├── CONFIGURATION.md           # All environment variables
    ├── AUTOMATION.md              # Reminders & week lifecycle
    ├── DATABASE.md                # Schema reference
    ├── TASK_TYPES.md              # All 22 task types
    ├── ADMIN_GUIDE.md             # Admin operations
    ├── ARCHITECTURE.md            # Technical internals
    ├── DEPLOYMENT.md              # Production deployment guide
    ├── TROUBLESHOOTING.md         # Common problems & fixes
    ├── FAQ.md                     # Frequently asked questions
    ├── UV_SETUP.md                # uv package manager guide
    ├── CHANGELOG.md               # Version history
    ├── RELEASE_NOTES.md           # v1.0.0 release notes
    └── images/
        ├── architecture.svg       # Architecture diagram
        ├── week-flow.svg          # Weekly timeline diagram
        └── demo-screenshot.svg    # Bot interface mockup
```

---

## Key Files — Where to Start

| Goal | File |
|---|---|
| Understand the bot | `src/bot.py` |
| Change task behavior | `src/handlers/task_handlers.py` |
| Change reminders | `src/reminders.py` |
| Change week schedule | `src/week_manager.py` |
| Add/edit tasks | `scripts/populate_db.py` |
| Change menus | `src/menus.py` |
| Database models | `src/models.py` |
| Environment settings | `src/config.py` + `.env` |

---

## Data Flow

```
User taps button in Telegram
        │
        ▼
bot.py::handle_callback()
        │
        ├── Checks private/group
        ├── Parses callback data (action:sub:id)
        │
        ▼
handlers/ module
        │
        ├── Queries DB via get_db() + SQLAlchemy
        ├── Updates task_instances / completion_log
        │
        ▼
bot.py::notify_group()     →   Group chat message
Telegram reply to user     →   Private chat confirmation
```

---

## Development Entry Points

```bash
make start          # Run bot (uv run python src/bot.py)
make populate       # Seed database (scripts/populate_db.py)
make test           # Verify installation (scripts/test_setup.py)
make reset          # Wipe database (scripts/reset_db.py)
```
