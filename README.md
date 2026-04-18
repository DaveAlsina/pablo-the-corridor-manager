# Pablo: The Corridor Manager 🧹

<p align="center">
  <img src="./docs/pablito.png" alt="Pablito the Corridor Manager" width="300"/>
</p>

<p align="center">
  <em>trust on pablito, he knows what to do.</em>
</p>

<p align="center">
  <img src="./docs/images/demo.gif" alt="Bot demo" width="600"/>
</p>

---

A Telegram bot for managing shared corridor cleaning tasks. Pablito helps groups of flatmates track who cleaned what, sends automated reminders, handles weekly cycles automatically, and keeps everyone accountable — with a bit of Colombian flair.

## ✨ Features

| Feature | Status |
|---|---|
| User registration via `/start` | ✅ |
| Interactive inline-button menus | ✅ |
| Task completion tracking | ✅ |
| Task amendment (undo) | ✅ |
| Weekly status reports | ✅ |
| Task instructions on demand | ✅ |
| Personal statistics | ✅ |
| Task opt-out system | ✅ |
| Corridor map | ✅ |
| Scheduled reminders (Tue + Fri) | ✅ |
| Automatic week generation (Sunday night) | ✅ |
| Automatic week closing + summary | ✅ |
| PostgreSQL database | ✅ |
| Private/group chat separation | ✅ |

## 🚀 Quick Start

```bash
git clone https://github.com/your-username/pablo-the-corridor-manager
cd pablo-the-corridor-manager
cp .env.example .env
# Edit .env with your bot token and chat ID
make setup
make install
make populate
make start
```

→ Full guide: [docs/QUICKSTART.md](docs/QUICKSTART.md)  
→ First time? Start here: [docs/GET_STARTED.md](docs/GET_STARTED.md)

## 📋 Commands

### Group Chat (public)
| Command | Description |
|---|---|
| `/start` | Register and show menu |
| `/menu` | Show interactive menu |
| `/status` | This week's task overview |
| `/tasks` | List all task types |
| `/whooptedout` | See who's opted out of what |
| `/help` | Help message |

### Private Chat (full access)
| Command | Description |
|---|---|
| All group commands | + everything below |
| `/mystats` | Your personal statistics |
| `/map` | Corridor map with task locations |
| `/optout <task> <reason>` | Opt out of a task |

→ Full reference: [docs/COMMANDS.md](docs/COMMANDS.md)

## 🏗️ Architecture

```
pablo-the-corridor-manager/
├── src/
│   ├── bot.py              # Main bot — command & callback routing
│   ├── models.py           # SQLAlchemy database models (7 tables)
│   ├── database.py         # DB connection utilities
│   ├── config.py           # Settings from .env
│   ├── menus.py            # Inline keyboard builders
│   ├── reminders.py        # Scheduled Tue/Fri reminders
│   ├── week_manager.py     # Automatic week rollover (Sunday)
│   └── handlers/
│       ├── task_handlers.py     # Complete, amend, ask flows
│       ├── info_handlers.py     # Status, stats, map, tasks list
│       └── optout_handlers.py   # Opt-out flow
├── scripts/
│   ├── populate_db.py      # Initialize with 22 task types
│   ├── reset_db.py         # Drop all data
│   └── test_setup.py       # Verify installation
├── alembic/                # Database migrations
├── docs/                   # Documentation
├── media/                  # Corridor images
├── docker-compose.yml      # PostgreSQL + pgAdmin
├── pyproject.toml          # Python project (managed with uv)
└── Makefile                # Common commands
```

→ Detailed breakdown: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)  
→ Technical architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## ⚙️ Automation

Pablito runs three background jobs automatically:

- **Tuesday 10:00 & 18:00** — Mid-week reminder with progress bar
- **Friday 10:00 & 18:00** — Final reminder before Sunday deadline
- **Sunday 23:59** — Week closes, summary sent, new week opens

→ Details: [docs/AUTOMATION.md](docs/AUTOMATION.md)

## 🗄️ Database

Seven tables: `people`, `task_types`, `task_opt_outs`, `weeks`, `task_instances`, `completion_log`, `penalties`

→ Full schema: [docs/DATABASE.md](docs/DATABASE.md)

## ⚙️ Configuration

All settings go in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=-1001234567890
POSTGRES_PASSWORD=choose_secure_password
# Optional
LOG_LEVEL=INFO
WEEK_DEADLINE_DAY=sunday
```

→ All options: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

## 📚 Documentation

| File | Description |
|---|---|
| [QUICKSTART.md](docs/QUICKSTART.md) | Get running in 5 minutes |
| [GET_STARTED.md](docs/GET_STARTED.md) | Detailed first-time setup |
| [COMMANDS.md](docs/COMMANDS.md) | Full command & button reference |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | All environment variables |
| [AUTOMATION.md](docs/AUTOMATION.md) | Reminders & week management |
| [DATABASE.md](docs/DATABASE.md) | Database schema reference |
| [TASK_TYPES.md](docs/TASK_TYPES.md) | All 22 task types |
| [ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) | Admin operations |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common problems & fixes |
| [FAQ.md](docs/FAQ.md) | Frequently asked questions |
| [UV_SETUP.md](docs/UV_SETUP.md) | uv package manager guide |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history |
| [RELEASE_NOTES.md](docs/RELEASE_NOTES.md) | v1.0.0 release notes |

## 🛠️ Development

```bash
make help       # List all commands
make setup      # First-time setup
make install    # Install dependencies (uv)
make start      # Run the bot
make populate   # Seed database
make reset      # Wipe database
make test       # Verify installation
make logs       # Follow PostgreSQL logs
```

Requires: Python 3.12+, Docker, [uv](https://docs.astral.sh/uv/)

→ Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🗺️ Roadmap

### v1.1.0 — Admin Controls
- [ ] `/closeweek` — manually close the current week
- [ ] `/newweek` — manually open a new week
- [ ] Admin user roles

### v1.2.0 — Accountability
- [ ] Penalty calculation and tracking
- [ ] Photo evidence for task completion
- [ ] Leaderboard (`/leaderboard`)

### v2.0.0 — Analytics
- [ ] Grafana dashboard
- [ ] Time-series analysis (procrastinated tasks, patterns)
- [ ] CSV/JSON export

## 📄 License

MIT — see [LICENSE](LICENSE)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 🔒 Security

See [SECURITY.md](SECURITY.md)
