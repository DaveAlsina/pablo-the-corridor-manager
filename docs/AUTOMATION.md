# Automation

Pablito manages the full weekly cycle automatically. Once started, no manual intervention is needed under normal operation.

---

## Weekly Timeline

```
Monday         Tuesday          Wednesday        Friday            Sunday
00:00          10:00 + 18:00                     10:00 + 18:00     23:59
  |                |                                  |               |
  |         Mid-week reminder                  Final reminder    Week closes
  |         (progress + who                   (deadline urgent)   Summary sent
New week     hasn't helped)                                       New week opens
announced
```

---

## Reminders

**File:** `src/reminders.py`

Sent twice on **Tuesday** and twice on **Friday**:
- 10:00 AM
- 18:00 PM

### Content

If tasks remain:
```
📢 Task Reminder

⏰ Due in 3 days
Deadline: Sunday, April 20 at 23:59

📊 Progress: ████░░░░░░ 8/22
🔴 14 tasks still need to be done!

💭 Haven't contributed yet:
Pablo, María, Luisa

¡Hagámosle pues! 💪
```

If all tasks are done:
```
🎉 All tasks completed!

Great work everyone! Time to relax 😎🍹
```

### Configuration

Edit constants at the top of `src/reminders.py`:

```python
REMINDER_DAYS = [1, 4]        # Tuesday=1, Friday=4 (0=Monday)
REMINDER_TIMES = [
    time(10, 0),               # 10:00 AM
    time(18, 0),               # 6:00 PM
]
DEADLINE_DAY = 6               # Sunday (used for deadline display)
```

---

## Week Closing & Summary

**File:** `src/week_manager.py`

Every **Sunday at 23:59**, the bot checks if the active week's deadline has passed. If yes:

1. Generates a summary message
2. Sends it to the group
3. Marks the week as `closed=True` in the database
4. Creates a new week immediately

### Summary Format

```
📅 Week 16/2026 Summary

📊 Progress: 18/22 tasks (81%)
⚠️ 4 tasks were not completed.

🌟 Thank you to our contributors:
🏆 Casimiro - 8 tasks
⭐ María - 5 tasks
✅ Luisa - 5 tasks

_Thanks to you, the corridor is a better place!_ 🏠✨

💭 We missed you this week:
Pablo, Andrés

_We would love to see you participate next week!_

➡️ New week starting now! Let's keep our corridor clean! 🧹
```

Contributor emojis:
- 🏆 5+ tasks
- ⭐ 3–4 tasks
- ✅ 1–2 tasks

### New Week Announcement

```
🆕 New Week Started!

📅 Week 17/2026
⏰ Deadline: Sunday, April 27 at 23:59
📋 Tasks to complete: 22

Let's make this week great! ¡Hagámosle pues! 💪
```

### Configuration

Edit constants at the top of `src/week_manager.py`:

```python
ROLLOVER_CHECK_TIME = (23, 59)   # Time to check daily (24h)
AUTO_CREATE_NEW_WEEK = True       # Create new week automatically
NEW_WEEK_DEADLINE_DAY = 6         # 6=Sunday
NEW_WEEK_DEADLINE_TIME = (23, 58) # 11:58 PM
```

---

## Manual Week Management

The `force_week_rollover()` function in `src/week_manager.py` allows triggering a rollover manually. This is useful for testing or correcting a missed rollover.

> ⚠️ Admin bot commands (`/closeweek`, `/newweek`) are planned for **v1.1.0** but not yet available as commands. Currently, this function must be called from Python directly.

```python
# Python REPL or script
import asyncio
from src.week_manager import force_week_rollover
from telegram.ext import Application
from src.config import settings

app = Application.builder().token(settings.telegram_bot_token).build()
async def run():
    await app.initialize()
    result = await force_week_rollover(app, int(settings.telegram_chat_id))
    print(result)

asyncio.run(run())
```

---

## How Jobs Are Registered

Both `setup_reminders()` and `setup_week_rollover()` are called from `src/bot.py` during `CorridorBot.__init__()`. The `python-telegram-bot` job queue (backed by APScheduler) handles scheduling.

```python
# src/bot.py — CorridorBot.__init__
setup_reminders(self.app, self.group_chat_id)
setup_week_rollover(self.app, self.group_chat_id)
```

Jobs persist as long as the bot process is running. Restarting the bot re-registers all jobs from scratch.
