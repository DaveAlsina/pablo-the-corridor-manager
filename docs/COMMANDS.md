# Command Reference

Complete reference for all commands and interactive buttons.

---

## Availability

| Context | What you get |
|---|---|
| Group chat | Public commands only — status, tasks, opt-out info |
| Private chat | Full access — complete tasks, stats, map, opt-out |

Sensitive actions redirect to private chat automatically with a button.

---

## Commands

### `/start`
Registers you if you're new, or welcomes you back. Opens the interactive menu.

**Available:** Group + Private

---

### `/menu`
Opens the interactive inline menu for the current chat context.

**Available:** Group + Private

---

### `/help`
Shows a summary of available commands depending on whether you're in group or private chat.

**Available:** Group + Private

---

### `/status`
Shows the current week's status:
- Week number and deadline
- Progress bars per category
- Last 5 completed tasks
- Who hasn't contributed yet

**Available:** Group + Private  
**Also via:** Menu button → 📋 View Status

---

### `/tasks`
Lists all task types grouped by category, with status icons (✅ done / ⏳ pending).

**Available:** Group + Private  
**Also via:** Menu button → 📝 View Tasks

---

### `/mystats`
Shows your personal statistics:
- Tasks completed this week
- All-time total
- Breakdown by category

**Available:** Private only  
**Also via:** Menu button → 📊 My Stats

---

### `/map`
Sends the corridor map image showing task locations.

**Available:** Private only  
**Also via:** Menu button → 🗺️ Map

---

### `/whooptedout`
Shows all active opt-outs: who is exempt from which task and why.

**Available:** Group + Private  
**Also via:** Menu button → 👁️ Who Opted Out

---

### `/optout <task_name> <reason>`
Opts you out of a specific task type. Opt-outs are permanent until an admin removes them.

**Available:** Private only  
**Examples:**
```
/optout Fridge 1 I have my own fridge in my room
/optout Kitchen A I don't use the communal kitchen
```

The task name is matched case-insensitively with partial matching (`Fridge` matches `Fridge 1`, `Fridge 2`, etc. — be specific).

---

## Interactive Menus

The bot uses inline keyboards. Open with `/menu` or `/start`.

### Private Menu Buttons

| Button | Action |
|---|---|
| 📋 View Status | Current week overview |
| ✅ Complete Task | Start task completion flow |
| ❌ Amend Task | Undo a completion |
| ❓ Ask Instructions | Get how-to guide for a task |
| 🚫 Opt Out | Start opt-out flow |
| 📊 My Stats | Personal statistics |
| 🗺️ Map | Corridor map |
| 📝 View Tasks | Full task list |
| 👁️ Who Opted Out | Current exemptions |
| ❓ Help | Help message |

### Group Menu Buttons

| Button | Action |
|---|---|
| 📋 View Status | Current week overview |
| 📝 View Tasks | Full task list |
| 👁️ Who Opted Out | Current exemptions |
| 🔒 + More... | Opens private chat for full access |

---

## Task Completion Flow (Private)

1. Tap **✅ Complete Task**
2. Select a **category** (Toilet 🚽, Kitchen 🍳, etc.)
3. Select a **specific task** from pending ones
4. Confirmation shown in private + notification sent to group

Group notification format:
```
✅ Casimiro completed: Toilet 1
📊 14 remaining, hagamole pues!
```

---

## Task Amendment Flow (Private)

1. Tap **❌ Amend Task**
2. Select a **category**
3. Select a **completed task** to undo
4. Confirmation shown + group notified

Use this to correct a mistake (wrong task marked, etc.).

---

## Automated Messages (no command needed)

Sent automatically to the group by Pablito:

| Trigger | Message |
|---|---|
| Tuesday 10:00 + 18:00 | Task reminder with progress |
| Friday 10:00 + 18:00 | Final reminder before deadline |
| Sunday 23:59 | Week summary + rankings |
| Sunday 23:59 +1s | New week announcement |
| Any task completion | "X completed: Task Name, N remaining" |
| All tasks done | "🎉 Week complete!" celebration |
