"""Corridor Cleaning Bot - Main Implementation."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

from src.config import settings
from src.database import get_db
from src.models import Person, TaskType, TaskInstance, Week, TaskOptOut, CompletionLog

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.log_level)
)
logger = logging.getLogger(__name__)

category_ammounts = {
    "toilet": 2,
    "shower": 2,
    "kitchen": 3,
    "fridge": 2,
    "hallway": 1,
    "laundry": 1,
    "trash": 2,
    "other": 1
}
            
category_emojis = {
    "toilet": "🚽",
    "shower": "🚿",
    "kitchen": "🍳",
    "fridge": "❄️",
    "hallway": "🚪",
    "laundry": "🧺",
    "trash": "🗑️",
    "other": "📦"
}


class CorridorBot:
    """Main bot class."""
    
    def __init__(self):
        """Initialize the bot."""
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command handlers."""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("complete", self.cmd_complete))
        self.app.add_handler(CommandHandler("done", self.cmd_complete))  # Alias
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("ask", self.cmd_ask))
        self.app.add_handler(CommandHandler("tasks", self.cmd_tasks))
        self.app.add_handler(CommandHandler("mystats", self.cmd_my_stats))
        self.app.add_handler(CommandHandler("map", self.cmd_show_map))  
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register or welcome a user."""
        user = update.effective_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            
            if not person:
                # Register new user
                person = Person(
                    telegram_id=user.id,
                    name=user.first_name,
                    username=user.username
                )
                db.add(person)
                db.commit()
                
                message = (
                    f"Bienvenido Mijo 😉! You're now registered {user.first_name}.\n\n"
                    f"Available commands:\n"
                    f"/status - View this week's task status\n"
                    f"/tasks - List all available tasks\n"
                    f"/complete <task> - Mark a task as complete\n"
                    f"/ask <task> - Get task instructions\n"
                    f"/mystats - View your statistics\n"
                    f"/help - Show this help message"
                )
            else:
                message = (
                    f"👋 Quiubo papi, bien o no?, bro/sis {person.name}!\n\n"
                    f"Use /status to see this week's tasks or /help for all commands."
                )
        
        await update.message.reply_text(message)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message."""
        help_text = (
            "🤖 *Pablito's Corridor Manager - Commands*\n\n"
            "*Task Management:*\n"
            "/status - View this week's task status\n"
            "/tasks - List all available tasks\n"
            "/complete `<task>` - Mark a task complete\n"
            "  Example: `/complete Toilet 1`\n"
            "/done `<task>` - Same as /complete\n\n"
            "*Information:*\n"
            "/ask `<task>` - Get task instructions\n"
            "/mystats - View your personal stats\n\n"
            "*General:*\n"
            "/start - Register or get started\n"
            "/help - Show this message\n\n"
            "💡 Tip: Task names are case-insensitive and can be partial matches!"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_complete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mark a task as complete."""
        if not context.args:
            await update.message.reply_text(
                "❌ Papi ¿y qué tarea hizo o qué?\nPlease specify a task!\n\n"
                "Usage: `/complete <task_name>`\n"
                "Example: `/complete Toilet 1`\n\n"
                "Use /tasks to see all available tasks.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        task_query = " ".join(context.args)
        user = update.effective_user
        
        with get_db() as db:
            # Get current week
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            if not current_week:
                await update.message.reply_text(
                    "❌ No active week found. Contact an administrator."
                )
                return
            
            # Get person
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            if not person:
                await update.message.reply_text(
                    "❌🔫 You're not registered! Use /start to register first."
                )
                return
            
            # Find matching task instance
            task_instance = (
                db.query(TaskInstance)
                .join(TaskType)
                .filter(
                    TaskInstance.week_id == current_week.id,
                    TaskInstance.status == "pending",
                    TaskType.name.ilike(f"%{task_query}%")
                )
                .first()
            )
            
            if not task_instance:
                # Check if task exists but is already completed
                completed_task = (
                    db.query(TaskInstance)
                    .join(TaskType)
                    .filter(
                        TaskInstance.week_id == current_week.id,
                        TaskInstance.status == "completed",
                        TaskType.name.ilike(f"%{task_query}%")
                    )
                    .first()
                )
                
                if completed_task:
                    completer = db.query(Person).get(completed_task.completed_by)
                    await update.message.reply_text(
                        f"❌ '{completed_task.task_type.name}' was already completed by {completer.name}.\n\n"
                        f"Use /status to see remaining tasks."
                    )
                else:
                    await update.message.reply_text(
                        f"❌ Task matching '{task_query}' not found.\n\n"
                        f"Use /tasks to see all available tasks."
                    )
                return
            
            # Check if person opted out of this task
            opt_out = (
                db.query(TaskOptOut)
                .filter_by(person_id=person.id, task_type_id=task_instance.task_type_id)
                .first()
            )
            
            if opt_out:
                await update.message.reply_text(
                    f"⚠️ You've opted out of '{task_instance.task_type.name}'.\n"
                    f"Reason: {opt_out.reason}\n\n"
                    f"If this is a mistake, contact an administrator."
                )
                return
            
            # Mark as complete
            task_instance.status = "completed"
            task_instance.completed_by = person.id
            task_instance.completed_at = datetime.now()
            
            # Log the completion
            log = CompletionLog(
                task_instance_id=task_instance.id,
                person_id=person.id,
                action="completed",
                message_id=update.message.message_id
            )
            db.add(log)
            db.commit()
            
            # Get remaining tasks
            completed = (
                db.query(TaskInstance)
                .filter_by(week_id=current_week.id, status="completed")
                .count()
            )
            total = sum([category_ammounts.get(cat, 1) for cat in category_ammounts.keys()])
            remaining = total - completed

            
            # Get personal stats for this week
            personal_count = (
                db.query(TaskInstance)
                .filter_by(week_id=current_week.id, completed_by=person.id)
                .count()
            )
            
            # Send confirmation
            message = (
                f"Eso es lo que nececitamos mijo!\n"
                f"✅ *Great job, {person.name}!*\n\n"
                f"Task completed: *{task_instance.task_type.name}*\n"
                f"Your tasks this week: *{personal_count}*\n\n"
                f"📊 Remaining tasks: *{remaining}*\n\n"
                f"Use /status to see what's left."
            )
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # Notify group (if this is a group chat)
            if update.effective_chat.type in ["group", "supergroup"]:
                if remaining <= 0:
                    group_message = (
                        f"🎉🎉🎉 ¡Mis amores! {person.name} Week Done! *{task_instance.task_type.name}*!\n"
                        f"Thank you very much for all your effort, time to chill 😎🍹"
                    )
                else:
                    group_message = (
                        f"✅ Mijitos {person.name} completed: *{task_instance.task_type.name}*\n"
                        f"📊 {remaining} tasks remaining, hagamole pues!"
                    )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=group_message,
                    parse_mode=ParseMode.MARKDOWN
                )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weekly task status."""
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if not current_week:
                await update.message.reply_text(
                    "❌ No active week found. Contact an administrator."
                )
                return
            
            # Get all task instances for the week
            all_instances = (
                db.query(TaskInstance)
                .filter_by(week_id=current_week.id)
                .join(TaskType)
                .order_by(TaskType.category, TaskType.name)
                .all()
            )
            
            completed = [t for t in all_instances if t.status == "completed"]
            
            # Build message
            message = (
                f"📅 *Week {current_week.week_number}/{current_week.year}*\n"
                f"⏰ Deadline: {current_week.deadline.strftime('%A, %B %d at %H:%M')}\n\n"
            )
            
            # Progress bar by category
            message += "📈 *Progress by Category*\n"
            
            by_category = {}
            for task in all_instances:
                category = task.task_type.category or "other"
                if category not in by_category:
                    by_category[category] = {"completed": 0, "total": 0}
                by_category[category]["total"] = category_ammounts.get(category, 1)
                if task.status == "completed":
                    by_category[category]["completed"] += 1
            
            for category in sorted(by_category.keys()):
                emoji = category_emojis.get(category, "📦")
                stats = by_category[category]
                progress = int((stats["completed"] / stats["total"]) * 10) if stats["total"] > 0 else 0
                progress_bar = "█" * progress + "░" * (10 - progress)
                message += f"{emoji} {category.title()}: {progress_bar} {stats['completed']}/{stats['total']} \n"
            
            # Overall progress
            total = sum([category_ammounts.get(cat, 1) for cat in by_category.keys()])
            completed_count = len(completed)
            if total > 0:
                progress = int((completed_count / total) * 10)
                progress_bar = "█" * progress + "░" * (10 - progress)
                message += f"\n📊 *Overall*: {progress_bar} {completed_count}/{total}\n\n"
            else:
                message += f"Progress: No tasks assigned yet\n\n"
            
            # Completed tasks (show last 5)
            message += f"✅ *Completed ({completed_count})*\n"
            for task in completed[-5:]:
                completer = db.query(Person).get(task.completed_by)
                message += f"  • {task.task_type.name} - {completer.name}\n"
            if completed_count > 5:
                message += f"  ... and {completed_count - 5} more\n"
            
            # Pending tasks (show first 10)
            done = all(by_category[cat]["completed"] >= by_category[cat]["total"] for cat in by_category)
            if not done:
                message += f"\n⏳ *Pending ({total - completed_count})*\n"
            else:
                message += f"\n🎉 All tasks completed! Time to relax! 😎🍹\n"
            
            # Suggest candidates (people who haven't contributed)
            completed_by_ids = [t.completed_by for t in completed if t.completed_by]
            active_people = db.query(Person).filter_by(active=True).all()
            not_contributed = [p for p in active_people if p.id not in completed_by_ids]
            
            if not done and not_contributed:
                message += f"\n ¿Y entonces qué? ¿nos vamos a quedar viendo pa' lo alto? 😡🔪"
                message += f"\n💭 *Haven't contributed yet:* "
                message += ", ".join([p.name for p in not_contributed])
            elif done and not_contributed:
                message += f"\n🎉 *All tasks done!* But hey, {', '.join([p.name for p in not_contributed])}, you didn't contribute this week! \n **Why?**"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all available task types."""
        with get_db() as db:
            tasks = db.query(TaskType).order_by(TaskType.category, TaskType.name).all()
            
            # Group by category
            by_category = {}
            for task in tasks:
                category = task.category or "other"
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(task)
            
            message = "📋 *All Available Tasks*\n\n"
            message += "Complete tasks using `/complete <task>`\n\n"
            
            
            for category, tasks in sorted(by_category.items()):
                emoji = category_emojis.get(category, "📦")
                get_aiming_ammount = category_ammounts.get(category, 1)

                message += f"{emoji} *{category.title()}* [Complete {get_aiming_ammount} task(s) per week]\n"
                for task in tasks:
                    duration = f" ({task.estimated_duration_minutes}min)" if task.estimated_duration_minutes else ""
                    message += f"  • {task.name}{duration}\n"
                message += "\n"
            
            message += "💡 Use `/ask <task>` for detailed instructions"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get task instructions."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify a task!\n\n"
                "Usage: `/ask <task_name>`\n"
                "Example: `/ask Toilet 1`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        task_query = " ".join(context.args)
        
        with get_db() as db:
            task_type = (
                db.query(TaskType)
                .filter(TaskType.name.ilike(f"%{task_query}%"))
                .first()
            )
            
            if not task_type:
                await update.message.reply_text(
                    f"❌ Task matching '{task_query}' not found.\n\n"
                    f"Use /tasks to see all available tasks."
                )
                return
            
            message = f"📋 *{task_type.name}*\n\n"
            
            if task_type.description:
                message += f"{task_type.description}\n\n"
            
            if task_type.instructions:
                message += f"*How to do it:*\n{task_type.instructions}\n\n"
            
            if task_type.location:
                message += f"📍 Location: {task_type.location}\n"
            
            if task_type.estimated_duration_minutes:
                message += f"⏱ Estimated time: {task_type.estimated_duration_minutes} minutes\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # TODO: Send media if available (implement later)
        # if task_type.media_file_id:
        #     await context.bot.send_document(...)
    
    async def cmd_my_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show personal statistics."""
        user = update.effective_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            
            if not person:
                await update.message.reply_text(
                    "❌ ¿Y usted quién es? You're not registered! Use /start to register first."
                )
                return
            
            # Current week stats
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if current_week:
                week_tasks = (
                    db.query(TaskInstance)
                    .filter_by(week_id=current_week.id, completed_by=person.id)
                    .join(TaskType)
                    .all()
                )
                
                message = (
                    f"📊 *Stats for {person.name}*\n\n"
                    f"*This Week (Week {current_week.week_number}):*\n"
                    f"Tasks completed: *{len(week_tasks)}*\n"
                )
                
                if week_tasks:
                    message += "\nTasks:\n"
                    for task in week_tasks:
                        message += f"  • {task.task_type.name}\n"
            else:
                message = f"📊 *Stats for {person.name}*\n\nNo active week found."
            
            # All-time stats
            all_time = (
                db.query(TaskInstance)
                .filter_by(completed_by=person.id)
                .count()
            )
            
            message += f"\n*All-Time:*\n"
            message += f"Total tasks completed: *{all_time}*\n"
            
            # Opted out tasks
            opt_outs = (
                db.query(TaskOptOut)
                .filter_by(person_id=person.id)
                .join(TaskType)
                .all()
            )
            
            if opt_outs:
                message += f"\n*Opted out of:*\n"
                for opt_out in opt_outs:
                    message += f"  • {opt_out.task_type.name}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_show_map(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show map of corridor areas."""

        # looks for image file in the 'media' folder and sends it
        media_path = project_root / "media" / "corridor-overview.jpg"
        print(f"Looking for media at: {media_path}")

        if media_path.exists():
            with open(media_path, "rb") as img_file:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img_file,
                    caption="🗺️ *Corridor Map*",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text(
                "❌ Corridor map image not found. Contact an administrator."
            )
        
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Pablito's Corridor Manager Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = CorridorBot()
    bot.run()
