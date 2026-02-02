# Project Structure

## Complete File Tree

```
corridor-bot/
│
├── 📋 Documentation
│   ├── README.md              # Complete documentation
│   ├── QUICKSTART.md          # 5-minute setup guide
│   └── PROJECT_STRUCTURE.md   # This file
│
├── ⚙️ Configuration
│   ├── .env.example           # Environment template
│   ├── .env                   # Your actual config (create from .example)
│   ├── .gitignore             # Git ignore rules
│   ├── docker-compose.yml     # PostgreSQL container setup
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini            # Database migration config
│   └── Makefile               # Convenience commands
│
├── 🐍 Source Code (src/)
│   ├── __init__.py            # Package initialization
│   ├── bot.py                 # Main bot implementation (⭐ START HERE)
│   ├── models.py              # Database models (SQLAlchemy)
│   ├── database.py            # Database connection utilities
│   └── config.py              # Configuration management
│
├── 🛠️ Scripts (scripts/)
│   ├── __init__.py            # Package initialization
│   ├── populate_db.py         # Initialize database with data
│   ├── reset_db.py            # Reset database (dangerous!)
│   └── test_setup.py          # Verify installation
│
└── 🗄️ Database Migrations (alembic/)
    ├── env.py                 # Alembic environment
    ├── script.py.mako         # Migration template
    └── versions/              # Migration files (auto-generated)
```

## Key Files Explained

### 📋 Documentation

**README.md**
- Complete project documentation
- Architecture overview
- Full setup instructions
- Troubleshooting guide
- Development tips

**QUICKSTART.md**
- Get running in 5 minutes
- Step-by-step setup
- Common issues & fixes

### ⚙️ Configuration Files

**docker-compose.yml**
- Defines PostgreSQL service
- Defines pgAdmin service (optional)
- Volume configuration for data persistence

**.env.example → .env**
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_group_id
POSTGRES_PASSWORD=secure_password
```

**requirements.txt**
- python-telegram-bot (bot framework)
- SQLAlchemy (ORM)
- psycopg2 (PostgreSQL driver)
- APScheduler (for future scheduled tasks)
- pydantic (configuration management)

### 🐍 Source Code

**src/bot.py** ⭐
- Main entry point
- Command handlers: `/start`, `/complete`, `/status`, etc.
- Bot logic and user interaction

**src/models.py**
- Database schema definitions
- 7 tables: Person, TaskType, TaskOptOut, Week, TaskInstance, CompletionLog, Penalty
- Relationships and constraints

**src/database.py**
- Database connection setup
- Session management
- Context managers for safe database access

**src/config.py**
- Loads environment variables
- Provides typed configuration
- Database URL construction

### 🛠️ Scripts

**populate_db.py**
- Creates all 22 task types (toilets, showers, kitchen, etc.)
- Adds 3 test users (Alice, Bob, Charlie)
- Creates current week with all tasks
- Run once during setup

**reset_db.py**
- Drops all tables
- Recreates fresh schema
- ⚠️ Destructive! Use with caution

**test_setup.py**
- Verifies configuration loaded
- Tests database connection
- Checks tables exist and have data
- Validates current week setup

## Data Flow

### User Completes a Task

```
1. User sends: /complete Toilet 1
   ↓
2. bot.py → cmd_complete()
   ↓
3. Query database for:
   - Current active week
   - Person (from telegram_id)
   - TaskInstance (matching "Toilet 1", status="pending")
   ↓
4. Update TaskInstance:
   - status = "completed"
   - completed_by = person.id
   - completed_at = now()
   ↓
5. Create CompletionLog entry (audit trail)
   ↓
6. Commit to database
   ↓
7. Send confirmation to user
   ↓
8. Notify group chat
```

### Weekly Status Check

```
1. User sends: /status
   ↓
2. bot.py → cmd_status()
   ↓
3. Query database:
   - Get current Week (closed=False)
   - Get all TaskInstances for week
   - Count completed vs pending
   - Identify people who haven't contributed
   ↓
4. Format message with:
   - Progress bar
   - Completed tasks list
   - Pending tasks list
   - Non-contributors
   ↓
5. Send to user
```

## Database Schema

### Core Tables

**people** (corridor residents)
```sql
- id (PK)
- telegram_id (unique)
- name
- username
- joined_date
- active
```

**task_types** (task definitions)
```sql
- id (PK)
- name (unique)
- category (toilet/shower/kitchen/etc)
- description
- instructions
- media_file_id (for videos/photos)
- estimated_duration_minutes
- location
```

**task_instances** (specific tasks per week)
```sql
- id (PK)
- week_id (FK)
- task_type_id (FK)
- status (pending/completed/skipped)
- completed_by (FK to people)
- completed_at
- notes
```

**weeks** (weekly cycles)
```sql
- id (PK)
- year
- week_number
- start_date
- deadline
- closed
```

### Relationships

```
Person ──< TaskInstance (completed_by)
Week ──< TaskInstance
TaskType ──< TaskInstance

Person ──< TaskOptOut ──> TaskType
```

## Command Reference

### Make Commands (if available)

```bash
make setup      # Initial setup
make db-up      # Start PostgreSQL
make db-down    # Stop PostgreSQL
make populate   # Populate database
make reset      # Reset database
make test       # Run verification
make start      # Start bot
make clean      # Clean Python cache
make logs       # View PostgreSQL logs
```

### Direct Python Commands

```bash
# Setup
cp .env.example .env
docker-compose up -d
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
python scripts/populate_db.py
python scripts/reset_db.py
python scripts/test_setup.py

# Run
python src/bot.py
```

## Development Workflow

### Adding a New Command

1. Add handler in `src/bot.py`:
```python
async def cmd_newcommand(self, update, context):
    # Your logic here
    pass

# Register in _register_handlers()
self.app.add_handler(CommandHandler("newcommand", self.cmd_newcommand))
```

### Adding a New Task Type

```python
from src.database import get_db
from src.models import TaskType

with get_db() as db:
    task = TaskType(
        name="New Task",
        category="other",
        description="Description here",
        instructions="Step 1\nStep 2",
        estimated_duration_minutes=20
    )
    db.add(task)
```

### Querying the Database

```python
from src.database import get_db
from src.models import Person, TaskInstance, Week

with get_db() as db:
    # Get all people
    people = db.query(Person).all()
    
    # Get current week
    week = db.query(Week).filter_by(closed=False).first()
    
    # Get person's completed tasks
    tasks = db.query(TaskInstance).filter_by(
        week_id=week.id,
        completed_by=person.id
    ).all()
```

## Architecture Decisions

### Why PostgreSQL?
- ACID compliance for 15 concurrent users
- JSON fields for flexibility
- Better for analytics queries
- Easier to scale

### Why SQLAlchemy?
- Type-safe database operations
- Automatic relationship management
- Easy migrations with Alembic
- Pythonic query syntax

### Why Not [X]?
- **SQLite**: Not safe for concurrent writes
- **MongoDB**: Overkill, relational data fits better
- **MySQL**: PostgreSQL has better JSON support
- **Raw SQL**: More error-prone, harder to maintain

## Future Enhancements

### Phase 2 (Automation)
- [ ] Scheduled reminders
- [ ] Auto-generate weeks
- [ ] Auto-close weeks
- [ ] Penalty calculation

### Phase 3 (Analytics)
- [ ] Grafana dashboard
- [ ] Task difficulty ratings
- [ ] Procrastination analysis
- [ ] Leaderboards

### Phase 4 (Advanced)
- [ ] Photo verification
- [ ] Task swapping
- [ ] Points redemption
- [ ] Integration with building management

## Support

**Questions?**
1. Check QUICKSTART.md
2. Check README.md
3. Review this file
4. Inspect database with pgAdmin (localhost:5050)

**Common Issues?**
See README.md → Troubleshooting section

**Want to contribute?**
See README.md → Development section
