# Admin Guide

Operations for whoever manages the bot deployment.

---

## Day-to-Day: Nothing to Do

Under normal operation, Pablito is fully autonomous. The only admin intervention needed is:
- Restarting the bot after server reboots
- Managing opt-out requests
- Handling database issues

---

## Week Management

### Normal Flow (automatic)
Every Sunday at 23:59, Pablito:
1. Sends a week summary to the group
2. Closes the current week
3. Creates a new week with fresh task instances
4. Announces the new week

### Manual Rollover (when needed)

> ⚠️ Bot commands `/closeweek` and `/newweek` are planned for v1.1.0. Currently you must use the Python method below.

If the bot was down on Sunday and the rollover didn't happen:

```python
# Run from the project directory
uv run python - << 'PYEOF'
import asyncio
from src.week_manager import force_week_rollover
from src.config import settings
from telegram.ext import Application

async def run():
    app = Application.builder().token(settings.telegram_bot_token).build()
    await app.initialize()
    result = await force_week_rollover(app, int(settings.telegram_chat_id))
    print(result)
    await app.shutdown()

asyncio.run(run())
PYEOF
```

### Manually Create a New Week

```python
uv run python - << 'PYEOF'
import asyncio
from datetime import datetime, timedelta
from src.database import get_db
from src.models import Week, TaskInstance, TaskType

with get_db() as db:
    now = datetime.now()
    deadline = now + timedelta(days=(6 - now.weekday()) % 7 or 7)
    deadline = deadline.replace(hour=23, minute=58, second=59)
    
    week = Week(
        year=now.year,
        week_number=now.isocalendar()[1],
        start_date=now.date(),
        deadline=deadline,
        closed=False
    )
    db.add(week)
    db.flush()
    
    for task_type in db.query(TaskType).all():
        db.add(TaskInstance(task_type_id=task_type.id, week_id=week.id, status="pending"))
    
    db.commit()
    print(f"Created week {week.week_number}/{week.year}, deadline: {deadline}")
PYEOF
```

---

## Managing Opt-Outs

### View all opt-outs

```python
uv run python - << 'PYEOF'
from src.database import get_db
from src.models import TaskOptOut, Person, TaskType

with get_db() as db:
    for opt in db.query(TaskOptOut).all():
        person = db.query(Person).get(opt.person_id)
        task = db.query(TaskType).get(opt.task_type_id)
        print(f"{person.name} opted out of {task.name}: {opt.reason}")
PYEOF
```

### Remove an opt-out

```python
uv run python - << 'PYEOF'
from src.database import get_db
from src.models import TaskOptOut, Person, TaskType

with get_db() as db:
    person = db.query(Person).filter_by(telegram_id=123456789).first()
    task = db.query(TaskType).filter_by(name="Fridge 1").first()
    opt = db.query(TaskOptOut).filter_by(
        person_id=person.id, task_type_id=task.id
    ).first()
    if opt:
        db.delete(opt)
        db.commit()
        print("Opt-out removed")
    else:
        print("No opt-out found")
PYEOF
```

---

## Managing Users

### List all registered users

```python
uv run python - << 'PYEOF'
from src.database import get_db
from src.models import Person

with get_db() as db:
    for p in db.query(Person).all():
        status = "active" if p.active else "inactive"
        print(f"[{p.id}] {p.name} (@{p.username}) — Telegram: {p.telegram_id} — {status}")
PYEOF
```

### Deactivate a user

```python
uv run python - << 'PYEOF'
from src.database import get_db
from src.models import Person

with get_db() as db:
    person = db.query(Person).filter_by(telegram_id=123456789).first()
    person.active = False
    db.commit()
    print(f"Deactivated {person.name}")
PYEOF
```

---

## Database Maintenance

### Full reset (wipes everything)

```bash
make reset
make populate
```

> ⚠️ This deletes all completion history, weeks, and registrations. Only for fresh starts.

### Backup the database

```bash
docker exec pablo-postgres pg_dump -U corridor_admin corridor > backup_$(date +%Y%m%d).sql
```

### Restore from backup

```bash
docker exec -i pablo-postgres psql -U corridor_admin corridor < backup_20260418.sql
```

### Access PostgreSQL directly

```bash
docker exec -it pablo-postgres psql -U corridor_admin -d corridor
```

---

## Logs

### Bot logs

```bash
# If running directly
uv run python src/bot.py 2>&1 | tee pablito.log

# If running as systemd service
journalctl -u pablito -f
```

### PostgreSQL logs

```bash
make logs
# or
docker-compose logs -f postgres
```

---

## Restarting the Bot

### Manual restart

```bash
# Stop
Ctrl+C  (or kill the process)

# Start
make start
```

### After server reboot (systemd)

```bash
sudo systemctl restart pablito
sudo systemctl status pablito
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for systemd service setup.

---

## Sending a Manual Group Message

```python
uv run python - << 'PYEOF'
import asyncio
from src.config import settings
from telegram import Bot

async def send():
    bot = Bot(token=settings.telegram_bot_token)
    await bot.send_message(
        chat_id=settings.telegram_chat_id,
        text="📢 *Announcement from admin*\n\nThe bot will be down for maintenance tonight from 22:00–23:00.",
        parse_mode="Markdown"
    )
    print("Sent!")

asyncio.run(send())
PYEOF
```
