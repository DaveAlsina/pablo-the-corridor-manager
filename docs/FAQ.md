# Frequently Asked Questions

---

## General

**What is Pablito?**  
A Telegram bot that manages shared corridor cleaning tasks. It tracks who cleaned what, sends reminders, and handles weekly cycles automatically.

**Does it work for any flat/corridor?**  
Yes. The task types, number of tasks per category, and deadlines are all configurable. The default setup fits a 10–15 person student corridor in the Netherlands, but you can adapt it.

**Does anyone need to be tech-savvy to use it?**  
Only the person deploying it. Once running, residents interact entirely through Telegram buttons — no commands needed.

---

## Using the Bot

**How do I register?**  
Send `/start` to the bot in your corridor group or in a private message. That's it.

**Why can't I complete tasks in the group chat?**  
Task completion is private to prevent conflicts — two people completing the same task, or someone else seeing your actions before you confirm. The bot sends a notification to the group after you complete in private.

**I accidentally marked a task as done. Can I undo it?**  
Yes. In private chat, use the **❌ Amend Task** button (or tap the Amend option in the menu). This undoes the completion and notifies the group.

**I don't use the communal kitchen/fridge. Do I still have to clean it?**  
No. Use `/optout Kitchen A I don't use the communal kitchen` in private chat. An opt-out is recorded and the bot won't let you complete that task (and others won't see it as your responsibility).

**Can two people split a task?**  
No, each task instance has one completer. If you want to split effort, one person completes it and the other picks a different task.

**What happens if the week ends and tasks are still pending?**  
The week closes on Sunday at 23:59 regardless. A summary is sent showing what was and wasn't done. Incomplete tasks are not carried over — each week starts fresh.

---

## Automation

**Do I have to manually create each week?**  
No. Pablito creates a new week automatically every Sunday at 23:59, right after closing the previous one.

**When exactly do reminders go out?**  
Tuesday and Friday at 10:00 and 18:00 (server local time).

**What if the bot was offline on Sunday? Will it catch up?**  
Not automatically. You'll need to trigger the rollover manually. See [ADMIN_GUIDE.md](ADMIN_GUIDE.md#manual-rollover).

**Can I change the deadline day?**  
Yes. Edit `NEW_WEEK_DEADLINE_DAY` in `src/week_manager.py` (0=Monday … 6=Sunday). Existing weeks won't be affected.

---

## Opt-Outs

**Can I opt back in after opting out?**  
Not through the bot (for now). Ask your corridor admin to remove the opt-out from the database. See [ADMIN_GUIDE.md](ADMIN_GUIDE.md#remove-an-opt-out).

**Can I opt out of multiple tasks?**  
Yes, run `/optout` once per task.

**Are opt-outs visible to everyone?**  
Yes. `/whooptedout` shows all active opt-outs to anyone in the group.

---

## Data & Privacy

**What data does the bot store?**  
Your Telegram ID, first name, and @username. Plus the tasks you've completed.

**Is the data encrypted?**  
The database is local to your server — as secure as your server is. No data is sent to any third party beyond Telegram's API.

**Can I delete my data?**  
Ask your corridor admin to deactivate your account (`active = False`) or delete your `people` record.

---

## Technical

**What if PostgreSQL isn't running?**  
The bot will fail to start with a connection error. Run `docker-compose up -d` and wait 15 seconds before starting the bot.

**Can I run this on a Raspberry Pi?**  
Yes — this is exactly what Pablito runs on at home. Use the systemd service setup in [DEPLOYMENT.md](DEPLOYMENT.md).

**Does it support multiple corridors?**  
Not yet. Multi-corridor support is on the long-term roadmap.

**The bot is slow to respond — is that normal?**  
Very minor lag (<1s) is normal due to Telegram's webhook processing. If responses take several seconds, check your internet connection from the server.
