# 🚀 Deployment & Testing Guide

## Overview

This guide covers:
1. ✅ Pre-deployment checklist
2. 🏗️ Step-by-step deployment
3. 🧪 Testing with 2-3 people
4. 🐛 Troubleshooting
5. 📊 Monitoring and maintenance

---

## Part 1: Pre-Deployment Checklist

### ☑️ Requirements

- [ ] Python 3.10 or higher installed
- [ ] Docker and Docker Compose installed
- [ ] Telegram bot token from @BotFather
- [ ] Group chat ID where bot will operate
- [ ] At least 500MB free disk space
- [ ] Port 5432 available (PostgreSQL)
- [ ] Port 5050 available (pgAdmin, optional)

### ☑️ Verify Installation

```bash
python --version  # Should show 3.10+
docker --version
docker-compose --version
```

---

## Part 2: Step-by-Step Deployment

### Step 1: Prepare Environment (5 min)

```bash
# Navigate to project
cd corridor-bot

# Create .env from template
cp .env.example .env

# Edit .env (use nano, vim, or your preferred editor)
nano .env
```

**Required settings in .env:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
POSTGRES_PASSWORD=my_secure_password_here
```

**How to get Telegram Chat ID:**
1. Add bot to your group
2. Send a message: "Hello bot!"
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find: `"chat":{"id":-1001234567890}`
5. Copy that negative number

### Step 2: Start Database (2 min)

```bash
# Start PostgreSQL container
docker-compose up -d

# Wait 10 seconds for database to initialize
sleep 10

# Verify it's running
docker-compose ps
```

**Expected output:**
```
NAME              STATUS    PORTS
corridor-db       Up        0.0.0.0:5432->5432/tcp
corridor-pgadmin  Up        0.0.0.0:5050->80/tcp
```

### Step 3: Setup Python Environment (5 min)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify activation (prompt should show (venv))

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**This installs:**
- python-telegram-bot (bot framework)
- SQLAlchemy (database ORM)
- psycopg2 (PostgreSQL driver)
- APScheduler (scheduled tasks)
- pydantic (configuration)
- Other utilities

### Step 4: Initialize Database (2 min)

```bash
# Populate database with initial data
python scripts/populate_db.py
```

**Expected output:**
```
INFO - Creating task types...
INFO - Created 22 task types
INFO - Creating test people...
INFO - Created 3 test people
INFO - Creating test opt-outs...
INFO - Created test opt-outs
INFO - Creating current week...
INFO - Created week 5/2026 with 22 task instances
INFO - Database population completed successfully!
```

**This creates:**
- 22 task types (4 toilets, 4 showers, 3 kitchen tasks, 4 fridges, etc.)
- 3 test users (Alice, Bob, Charlie)
- Current week with all tasks in "pending" status
- Test opt-outs (Alice doesn't use communal fridges)

### Step 5: Verify Setup (1 min)

```bash
# Run verification tests
python scripts/test_setup.py
```

**All tests should pass:**
```
✅ PASS: Configuration
✅ PASS: Database Connection
✅ PASS: Database Tables
✅ PASS: Current Week
🎉 All tests passed! You're ready to run the bot.
```

**If any fail, see Troubleshooting section below.**

### Step 6: Start the Bot (1 min)

```bash
# Start bot (keep this terminal open)
python src/bot.py
```

**Expected output:**
```
INFO - Starting Corridor Bot...
INFO - Application started
INFO - Listening for updates...
```

**Keep this terminal running!** The bot needs to stay active to respond to messages.

---

## Part 3: Testing with 2-3 People

### Test User Profiles

The database includes 3 test users:

**Alice (telegram_id: 123456789)**
- Opted out of all 4 fridges (has private fridge)
- Can do: 18 tasks (all except fridges)

**Bob (telegram_id: 987654321)**
- No opt-outs
- Can do: All 22 tasks

**Charlie (telegram_id: 555555555)**
- No opt-outs
- Can do: All 22 tasks

### Testing Workflow

#### Test 1: Registration (All Users)

**Each tester:**
1. Open Telegram
2. Start private chat with your bot (search for bot name)
3. Send: `/start`

**Expected Response:**
```
🎉 Welcome <Name>! You're now registered.

Available commands:
/status - View this week's task status
/tasks - List all available tasks
/complete <task> - Mark a task as complete
...
```

**Verify in database:**
```bash
# In a new terminal (keep bot running)
docker exec -it corridor-db psql -U corridor_admin -d corridor -c "SELECT name, telegram_id FROM people;"
```

Should show your real Telegram users + 3 test users.

#### Test 2: View Status

**Command:** `/status`

**Expected Response:**
```
📅 Week 5/2026
⏰ Deadline: Friday, February 07 at 12:00

Progress: ░░░░░░░░░░ 0/22

✅ Completed (0)

⏳ Pending (22)
  • Toilet 1
  • Toilet 2
  • Shower A
  • Shower B
  ... (shows first 10)
  ... and 12 more

💭 Haven't contributed yet: Alice, Bob, Charlie, <YourName>
```

#### Test 3: List Tasks

**Command:** `/tasks`

**Expected Response:**
Shows all 22 tasks grouped by category with emojis.

#### Test 4: Get Task Instructions

**Command:** `/ask Toilet 1`

**Expected Response:**
```
📋 Toilet 1

Clean toilet on 1st floor

How to do it:
1. Clean toilet bowl with toilet cleaner
2. Wipe sink and mirror
3. Mop floor
4. Empty trash bin
5. Refill toilet paper if needed

📍 Location: 1st floor
⏱ Estimated time: 15 minutes
```

#### Test 5: Complete a Task (Primary Test)

**Tester 1 (e.g., Bob):**

**Command:** `/complete Toilet 1`

**Expected Response:**
```
✅ Great job, Bob!

Task completed: Toilet 1
Your tasks this week: 1

📊 Remaining tasks: 21

Use /status to see what's left.
```

**In group chat (if bot is in group):**
```
✅ Bob completed: Toilet 1
📊 21 tasks remaining
```

**Verify in database:**
```bash
docker exec -it corridor-db psql -U corridor_admin -d corridor \
  -c "SELECT tt.name, p.name as completed_by, ti.completed_at 
      FROM task_instances ti 
      JOIN task_types tt ON ti.task_type_id = tt.id 
      JOIN people p ON ti.completed_by = p.id 
      WHERE ti.status = 'completed';"
```

#### Test 6: View Personal Stats

**Command:** `/mystats`

**Expected Response:**
```
📊 Stats for Bob

This Week (Week 5):
Tasks completed: 1

Tasks:
  • Toilet 1

All-Time:
Total tasks completed: 1
```

#### Test 7: Try Completing Already Completed Task

**Tester 2 (e.g., Alice):**

**Command:** `/complete Toilet 1`

**Expected Response:**
```
❌ 'Toilet 1' was already completed by Bob.

Use /status to see remaining tasks.
```

#### Test 8: Test Opt-Out System

**Tester: Alice (who opted out of fridges):**

**Command:** `/complete Fridge 1`

**Expected Response:**
```
⚠️ You've opted out of 'Fridge 1'.
Reason: Has own fridge in room

If this is a mistake, contact an administrator.
```

#### Test 9: Partial Name Matching

**Command:** `/complete shower a`  (lowercase, partial)

**Expected Response:**
Should match "Shower A" and mark it complete.

#### Test 10: Invalid Task

**Command:** `/complete NonExistentTask`

**Expected Response:**
```
❌ Task matching 'NonExistentTask' not found.

Use /tasks to see all available tasks.
```

### Testing Matrix

| Tester | Tasks to Complete | Expected Outcome |
|--------|------------------|------------------|
| Person 1 | Toilet 1, Shower A, Kitchen A | ✅ All succeed |
| Person 2 | Toilet 1 (again), Toilet 2 | ❌ First fails, second succeeds |
| Person 3 (Alice) | Fridge 1, Hall S | ❌ First fails (opted out), second succeeds |

**After all tests, run:**
```bash
# See updated status
# In Telegram: /status

# Expected: 5-6 tasks completed, 16-17 pending
```

---

## Part 4: Troubleshooting

### Problem: Bot doesn't start

**Symptoms:**
```
ERROR - Invalid token
```

**Solution:**
1. Check `TELEGRAM_BOT_TOKEN` in `.env`
2. Verify token with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
3. Should return JSON with bot info

---

### Problem: Database connection fails

**Symptoms:**
```
ERROR - Database connection failed
```

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# If not running, start it
docker-compose up -d

# Wait 10 seconds
sleep 10

# Check logs
docker-compose logs postgres

# If issues, restart
docker-compose restart postgres
```

---

### Problem: "No active week found"

**Symptoms:**
Bot says: "No active week found"

**Solution:**
```bash
# Check database
docker exec -it corridor-db psql -U corridor_admin -d corridor \
  -c "SELECT * FROM weeks WHERE closed = false;"

# If empty, repopulate
python scripts/reset_db.py
python scripts/populate_db.py
```

---

### Problem: Bot in group doesn't respond

**Symptoms:**
Bot works in private chat but not in group

**Solutions:**
1. **Check Privacy Mode:**
   - Go to @BotFather
   - Send `/mybots`
   - Select your bot
   - Bot Settings → Group Privacy → Turn OFF

2. **Verify Chat ID:**
   - Check `TELEGRAM_CHAT_ID` in `.env` is correct
   - Should be negative number like `-1001234567890`

3. **Restart bot:**
   ```bash
   # Stop bot (Ctrl+C)
   # Start again
   python src/bot.py
   ```

---

### Problem: Tasks not showing

**Symptoms:**
`/tasks` returns empty or error

**Solution:**
```bash
# Check task types exist
docker exec -it corridor-db psql -U corridor_admin -d corridor \
  -c "SELECT COUNT(*) FROM task_types;"

# Should return 22
# If 0, repopulate
python scripts/populate_db.py
```

---

## Part 5: Monitoring & Maintenance

### Daily Checks

**Monitor bot process:**
```bash
# Check if bot is running
ps aux | grep "python src/bot.py"

# If not, restart
python src/bot.py
```

**Check database size:**
```bash
docker exec -it corridor-db psql -U corridor_admin -d corridor \
  -c "SELECT pg_size_pretty(pg_database_size('corridor'));"
```

### Weekly Tasks

**Check completion rates:**
```sql
-- Run in pgAdmin or psql
SELECT 
    w.week_number,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN ti.status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN ti.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM weeks w
JOIN task_instances ti ON w.id = ti.week_id
GROUP BY w.id, w.week_number
ORDER BY w.week_number DESC;
```

### Backup Database

```bash
# Create backup
docker exec corridor-db pg_dump -U corridor_admin corridor > backup_$(date +%Y%m%d).sql

# Restore backup (if needed)
cat backup_20260201.sql | docker exec -i corridor-db psql -U corridor_admin corridor
```

### Reset for New Week (Manual - Phase 1)

```bash
# Connect to database
docker exec -it corridor-db psql -U corridor_admin corridor

-- In psql:
-- Close current week
UPDATE weeks SET closed = true WHERE closed = false;

-- Create new week (adjust dates)
INSERT INTO weeks (year, week_number, start_date, deadline, closed)
VALUES (2026, 6, '2026-02-10', '2026-02-14 12:00:00', false);

-- Get the new week ID
SELECT id FROM weeks WHERE week_number = 6 AND year = 2026;

-- Create task instances for new week (replace 123 with actual week ID)
INSERT INTO task_instances (week_id, task_type_id, status)
SELECT 123, id, 'pending' FROM task_types;

\q
```

---

## Part 6: Success Criteria

### ✅ Deployment is successful when:

- [ ] Bot responds to `/start` in private chat
- [ ] Bot responds to `/status` showing current week
- [ ] Bot successfully marks tasks as complete
- [ ] Database correctly tracks completions
- [ ] Multiple users can interact simultaneously
- [ ] Opt-out system works (Alice can't do fridges)
- [ ] Status updates show accurate progress
- [ ] Personal stats reflect individual contributions

### ✅ Testing is complete when:

- [ ] All 10 test cases pass
- [ ] 2-3 real users successfully registered
- [ ] At least 5 tasks marked complete
- [ ] Status command shows accurate progress
- [ ] No errors in bot logs
- [ ] Database queries return expected data

---

## Next Steps After Testing

1. **Remove test users (optional):**
```bash
docker exec -it corridor-db psql -U corridor_admin corridor \
  -c "DELETE FROM people WHERE telegram_id IN (123456789, 987654321, 555555555);"
```

2. **Add real corridor members:**
   - Share bot link with corridor
   - Each person sends `/start`
   - Verify in database

3. **Configure opt-outs:**
   - Identify who has private fridges/kitchens
   - Add opt-outs manually or build admin command (Phase 2)

4. **Monitor first real week:**
   - Check participation rates
   - Gather feedback
   - Adjust task descriptions if needed

5. **Plan Phase 2:**
   - Scheduled reminders
   - Automated week management
   - Penalty system implementation

---

## Support Contacts

**Technical Issues:**
- Check README.md
- Check QUICKSTART.md  
- Review error logs: `docker-compose logs`

**Database Access:**
- pgAdmin: http://localhost:5050
- Direct psql: `docker exec -it corridor-db psql -U corridor_admin corridor`

**Emergency Reset:**
```bash
docker-compose down -v  # Remove volumes (data loss!)
docker-compose up -d
python scripts/populate_db.py
```

---

**Good luck with your deployment! 🚀**
