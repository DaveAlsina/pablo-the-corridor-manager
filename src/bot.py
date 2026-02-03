"""Corridor Cleaning Bot - Interactive Version with Menus."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
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

# Category configuration
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
    """Main bot class with interactive menus."""
    
    def __init__(self):
        """Initialize the bot."""
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command and callback handlers."""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("menu", self.cmd_menu))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("tasks", self.cmd_tasks))
        self.app.add_handler(CommandHandler("mystats", self.cmd_my_stats))
        self.app.add_handler(CommandHandler("map", self.cmd_show_map))
        self.app.add_handler(CommandHandler("whooptedout", self.cmd_who_opted_out))
        
        # Callback handler for button clicks
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
    
    def create_main_menu(self):
        """Create the main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📋 View Status", callback_data="status"),
                InlineKeyboardButton("✅ Complete Task", callback_data="complete:categories")
            ],
            [
                InlineKeyboardButton("❌ Amend Task", callback_data="amend:categories"),
                InlineKeyboardButton("❓ Ask Instructions", callback_data="ask:categories")
            ],
            [
                InlineKeyboardButton("🚫 Opt Out", callback_data="optout:categories"),
                InlineKeyboardButton("📊 My Stats", callback_data="mystats")
            ],
            [
                InlineKeyboardButton("🗺️ Show Map", callback_data="map"),
                InlineKeyboardButton("💡 Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_category_menu(self, action="complete"):
        """Create category selection menu with progress."""
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if not current_week:
                return None
            
            # Get task counts by category
            all_instances = (
                db.query(TaskInstance)
                .filter_by(week_id=current_week.id)
                .join(TaskType)
                .all()
            )
            
            by_category = {}
            for task in all_instances:
                category = task.task_type.category or "other"
                if category not in by_category:
                    by_category[category] = {"completed": 0, "total": 0}
                if action == "complete" and task.status == "pending":
                    by_category[category]["total"] += 1
                elif action == "amend" and task.status == "completed":
                    by_category[category]["total"] += 1
                else:
                    # For ask/optout, count all tasks
                    by_category[category]["total"] += 1
                
                if task.status == "completed":
                    by_category[category]["completed"] += 1
            
            # Create buttons (2 per row)
            keyboard = []
            row = []
            for category in sorted(by_category.keys()):
                if by_category[category]["total"] == 0:
                    continue  # Skip categories with no tasks
                
                emoji = category_emojis.get(category, "📦")
                stats = by_category[category]
                button_text = f"{emoji} {category.title()} ({stats['completed']}/{category_ammounts.get(category, 1)})"
                
                row.append(InlineKeyboardButton(
                    button_text,
                    callback_data=f"{action}:category:{category}"
                ))
                
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            
            if row:  # Add remaining button
                keyboard.append(row)
            
            # Add back button
            keyboard.append([InlineKeyboardButton("« Back to Menu", callback_data="menu")])
            
            return InlineKeyboardMarkup(keyboard)
    
    def create_task_menu(self, category, action="complete"):
        """Create task selection menu for a category."""
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if not current_week:
                return None
            
            # Get tasks for this category
            query = (
                db.query(TaskInstance)
                .join(TaskType)
                .filter(
                    TaskInstance.week_id == current_week.id,
                    TaskType.category == category
                )
            )
            
            # Filter by status based on action
            if action == "complete":
                query = query.filter(TaskInstance.status == "pending")
            elif action == "amend":
                query = query.filter(TaskInstance.status == "completed")
            # For ask/optout, show all tasks
            
            tasks = query.order_by(TaskType.name).all()
            
            if not tasks:
                return None
            
            # Create buttons (1 per row for readability)
            keyboard = []
            for task in tasks:
                task_type = task.task_type
                duration = f" - {task_type.estimated_duration_minutes}min" if task_type.estimated_duration_minutes else ""
                
                # Add status indicator
                status_emoji = "✅" if task.status == "completed" else "⏳"
                button_text = f"{status_emoji} {task_type.name}{duration}"
                
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"{action}:task:{task.id}"
                )])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("« Back to Categories", callback_data=f"{action}:categories")])
            
            return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all button clicks."""
        query = update.callback_query
        await query.answer()  # Acknowledge the click
        
        data = query.data
        parts = data.split(":")
        action = parts[0]
        
        # Route to appropriate handler
        if action == "menu":
            await self.show_main_menu(query)
        elif action == "status":
            await self.show_status_callback(query)
        elif action == "mystats":
            await self.show_stats_callback(query)
        elif action == "map":
            await self.show_map_callback(query)
        elif action == "help":
            await self.show_help_callback(query)
        elif action == "complete":
            await self.handle_complete_flow(query, parts)
        elif action == "amend":
            await self.handle_amend_flow(query, parts)
        elif action == "ask":
            await self.handle_ask_flow(query, parts)
        elif action == "optout":
            await self.handle_optout_flow(query, parts)
    
    async def show_main_menu(self, query):
        """Show the main menu."""
        text = (
            "🤖 *Pablito's Corridor Manager*\n\n"
            "Choose an action:"
        )
        await query.edit_message_text(
            text=text,
            reply_markup=self.create_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_complete_flow(self, query, parts):
        """Handle the complete task flow."""
        user = query.from_user
        
        if len(parts) == 2 and parts[1] == "categories":
            # Show category menu
            text = "✅ *Complete a Task*\n\nSelect a category:"
            keyboard = self.create_category_menu("complete")
            
            if not keyboard:
                await query.edit_message_text("❌ No active week found.")
                return
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "category":
            # Show tasks in category
            category = parts[2]
            emoji = category_emojis.get(category, "📦")
            text = f"✅ *Complete a Task*\n\n{emoji} {category.title()} - Select a task:"
            
            keyboard = self.create_task_menu(category, "complete")
            
            if not keyboard:
                await query.edit_message_text(
                    f"ℹ️ No pending tasks in {category}!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Back", callback_data="complete:categories")
                    ]])
                )
                return
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "task":
            # Complete the selected task
            await self.complete_task_by_id(query, int(parts[2]))
    
    async def complete_task_by_id(self, query, task_instance_id):
        """Complete a task by its instance ID."""
        user = query.from_user
        
        with get_db() as db:
            # Get person
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            if not person:
                await query.edit_message_text("❌ You're not registered! Use /start first.")
                return
            
            # Get task instance
            task_instance = db.query(TaskInstance).get(task_instance_id)
            if not task_instance or task_instance.status != "pending":
                await query.edit_message_text("❌ Task not found or already completed.")
                return
            
            # Check opt-out
            opt_out = (
                db.query(TaskOptOut)
                .filter_by(person_id=person.id, task_type_id=task_instance.task_type_id)
                .first()
            )
            
            if opt_out:
                await query.edit_message_text(
                    f"⚠️ You've opted out of '{task_instance.task_type.name}'.\n"
                    f"Reason: {opt_out.reason}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Back to Menu", callback_data="menu")
                    ]])
                )
                return
            
            # Mark as complete
            task_instance.status = "completed"
            task_instance.completed_by = person.id
            task_instance.completed_at = datetime.now()
            
            # Log
            log = CompletionLog(
                task_instance_id=task_instance.id,
                person_id=person.id,
                action="completed",
                message_id=query.message.message_id
            )
            db.add(log)
            db.commit()
            
            # Get stats
            current_week = db.query(Week).get(task_instance.week_id)
            completed = db.query(TaskInstance).filter_by(
                week_id=current_week.id, status="completed"
            ).count()
            total = sum([category_ammounts.get(cat, 1) for cat in category_ammounts.keys()])
            remaining = total - completed
            
            personal_count = db.query(TaskInstance).filter_by(
                week_id=current_week.id, completed_by=person.id
            ).count()
            
            # Send confirmation
            message = (
                f"Eso es lo que nececitamos mijo!\n"
                f"✅ *Great job, {person.name}!*\n\n"
                f"Task completed: *{task_instance.task_type.name}*\n"
                f"Your tasks this week: *{personal_count}*\n"
                f"📊 Remaining: *{remaining}*"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Complete Another", callback_data="complete:categories")],
                [InlineKeyboardButton("« Back to Menu", callback_data="menu")]
            ])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify group
            if query.message.chat.type in ["group", "supergroup"]:
                if remaining <= 0:
                    group_message = (
                        f"🎉🎉🎉 ¡Mis amores! {person.name} Week Done! *{task_instance.task_type.name}*!\n"
                        f"Time to chill 😎🍹"
                    )
                else:
                    group_message = (
                        f"✅ {person.name} completed: *{task_instance.task_type.name}*\n"
                        f"📊 {remaining} remaining, hagamole pues!"
                    )
                await query.message.reply_text(group_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_amend_flow(self, query, parts):
        """Handle the amend task flow."""
        if len(parts) == 2 and parts[1] == "categories":
            text = "❌ *Amend a Task*\n\nSelect a category:"
            keyboard = self.create_category_menu("amend")
            
            if not keyboard:
                await query.edit_message_text("ℹ️ No completed tasks to amend.")
                return
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "category":
            category = parts[2]
            emoji = category_emojis.get(category, "📦")
            text = f"❌ *Amend a Task*\n\n{emoji} {category.title()} - Select a task:"
            
            keyboard = self.create_task_menu(category, "amend")
            
            if not keyboard:
                await query.edit_message_text(
                    f"ℹ️ No completed tasks in {category} to amend!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Back", callback_data="amend:categories")
                    ]])
                )
                return
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "task":
            await self.amend_task_by_id(query, int(parts[2]))
    
    async def amend_task_by_id(self, query, task_instance_id):
        """Amend a task by its instance ID."""
        user = query.from_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            if not person:
                await query.edit_message_text("❌ You're not registered!")
                return
            
            task_instance = db.query(TaskInstance).get(task_instance_id)
            if not task_instance or task_instance.status != "completed":
                await query.edit_message_text("❌ Task not found or not completed.")
                return
            
            # Get original completer
            original_completer = db.query(Person).get(task_instance.completed_by)
            
            # Undo completion
            task_instance.status = "pending"
            task_instance.completed_by = None
            task_instance.completed_at = None
            
            # Log amendment
            log = CompletionLog(
                task_instance_id=task_instance.id,
                person_id=person.id,
                action="amended",
                message_id=query.message.message_id
            )
            db.add(log)
            db.commit()
            
            message = (
                f"✅ Task amended!\n\n"
                f"*{task_instance.task_type.name}* is now pending.\n"
                f"Was completed by: {original_completer.name}\n"
                f"Amended by: {person.name}"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Amend Another", callback_data="amend:categories")],
                [InlineKeyboardButton("« Back to Menu", callback_data="menu")]
            ])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify group
            if query.message.chat.type in ["group", "supergroup"]:
                group_message = (
                    f"⚠️ {person.name} amended *{task_instance.task_type.name}*\n"
                    f"(was completed by {original_completer.name})"
                )
                await query.message.reply_text(group_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_ask_flow(self, query, parts):
        """Handle the ask instructions flow."""
        if len(parts) == 2 and parts[1] == "categories":
            text = "❓ *Ask Instructions*\n\nSelect a category:"
            keyboard = self.create_category_menu("ask")
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "category":
            category = parts[2]
            emoji = category_emojis.get(category, "📦")
            text = f"❓ *Ask Instructions*\n\n{emoji} {category.title()} - Select a task:"
            
            keyboard = self.create_task_menu(category, "ask")
            
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif len(parts) == 3 and parts[1] == "task":
            await self.show_task_instructions(query, int(parts[2]))
    
    async def show_task_instructions(self, query, task_instance_id):
        """Show instructions for a task."""
        with get_db() as db:
            task_instance = db.query(TaskInstance).get(task_instance_id)
            if not task_instance:
                await query.edit_message_text("❌ Task not found.")
                return
            
            task_type = task_instance.task_type
            
            message = f"📋 *{task_type.name}*\n\n"
            
            if task_type.description:
                message += f"{task_type.description}\n\n"
            
            if task_type.instructions:
                message += f"*How to do it:*\n{task_type.instructions}\n\n"
            
            if task_type.location:
                message += f"📍 Location: {task_type.location}\n"
            
            if task_type.estimated_duration_minutes:
                message += f"⏱ Time: {task_type.estimated_duration_minutes} min\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Ask Another", callback_data="ask:categories")],
                [InlineKeyboardButton("« Back to Menu", callback_data="menu")]
            ])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_optout_flow(self, query, parts):
        """Handle opt-out flow (shows message about using command)."""
        # Opt-out requires a reason, so we direct to command
        text = (
            "🚫 *Opt Out of a Task*\n\n"
            "To opt out, use this command:\n"
            "`/optout <task> <reason>`\n\n"
            "*Example:*\n"
            "`/optout Fridge 1 I have my own fridge`\n\n"
            "Or use `/whooptedout` to see current opt-outs."
        )
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("« Back to Menu", callback_data="menu")
        ]])
        
        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_status_callback(self, query):
        """Show status via callback."""
        # Reuse existing status logic
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if not current_week:
                await query.edit_message_text("❌ No active week found.")
                return
            
            # Get progress summary (simplified for menu)
            all_instances = db.query(TaskInstance).filter_by(week_id=current_week.id).all()
            completed_count = len([t for t in all_instances if t.status == "completed"])
            total = sum([category_ammounts.get(cat, 1) for cat in category_ammounts.keys()])
            
            progress = int((completed_count / total) * 10) if total > 0 else 0
            progress_bar = "█" * progress + "░" * (10 - progress)
            
            message = (
                f"📅 *Week {current_week.week_number}/{current_week.year}*\n"
                f"⏰ Deadline: {current_week.deadline.strftime('%a, %b %d at %H:%M')}\n\n"
                f"📊 Progress: {progress_bar} {completed_count}/{total}\n\n"
                f"💡 Use `/status` for detailed view"
            )
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("« Back to Menu", callback_data="menu")
            ]])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_stats_callback(self, query):
        """Show personal stats via callback."""
        user = query.from_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            if not person:
                await query.edit_message_text("❌ You're not registered!")
                return
            
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if current_week:
                week_count = db.query(TaskInstance).filter_by(
                    week_id=current_week.id, completed_by=person.id
                ).count()
            else:
                week_count = 0
            
            all_time = db.query(TaskInstance).filter_by(completed_by=person.id).count()
            
            message = (
                f"📊 *Stats for {person.name}*\n\n"
                f"This week: *{week_count}* tasks\n"
                f"All-time: *{all_time}* tasks\n\n"
                f"💡 Use `/mystats` for detailed view"
            )
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("« Back to Menu", callback_data="menu")
            ]])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_map_callback(self, query):
        """Show map via callback."""
        media_path = project_root / "media" / "corridor-overview.jpg"
        
        if media_path.exists():
            with open(media_path, "rb") as img_file:
                await query.message.reply_photo(
                    photo=img_file,
                    caption="🗺️ *Corridor Map*",
                    parse_mode=ParseMode.MARKDOWN
                )
            # Edit original message
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("« Back to Menu", callback_data="menu")
            ]])
            await query.edit_message_text(
                "Map sent above! ⬆️",
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(
                "❌ Map not found.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Back to Menu", callback_data="menu")
                ]])
            )
    
    async def show_help_callback(self, query):
        """Show help via callback."""
        text = (
            "🤖 *Pablito's Corridor Manager*\n\n"
            "*Commands:*\n"
            "/menu - Show this interactive menu\n"
            "/status - Detailed weekly status\n"
            "/tasks - List all tasks\n"
            "/mystats - Your detailed stats\n"
            "/optout <task> <reason> - Opt out\n"
            "/whooptedout - See opt-outs\n"
            "/map - Show corridor map\n\n"
            "💡 Use the buttons for easy navigation!"
        )
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("« Back to Menu", callback_data="menu")
        ]])
        
        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # ========== Command Handlers ==========
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register user and show menu."""
        user = update.effective_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            
            if not person:
                person = Person(
                    telegram_id=user.id,
                    name=user.first_name,
                    username=user.username
                )
                db.add(person)
                db.commit()
                
                message = f"Bienvenido Mijo 😉! You're registered, {user.first_name}!\n\n"
            else:
                message = f"👋 Quiubo papi, {person.name}!\n\n"
        
        message += "Use the menu below:"
        await update.message.reply_text(
            message,
            reply_markup=self.create_main_menu()
        )
    
    async def cmd_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the main menu."""
        await update.message.reply_text(
            "🤖 *Pablito's Corridor Manager*\n\nChoose an action:",
            reply_markup=self.create_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help."""
        text = (
            "🤖 *Pablito's Corridor Manager*\n\n"
            "*Interactive Menu:*\n"
            "/menu - Show button menu\n"
            "/start - Register & show menu\n\n"
            "*Detailed Commands:*\n"
            "/status - Full weekly status\n"
            "/tasks - List all tasks\n"
            "/mystats - Your detailed stats\n"
            "/optout <task> <reason> - Opt out\n"
            "/whooptedout - See opt-outs\n"
            "/map - Show corridor map\n\n"
            "💡 Use the buttons for easy task management!"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed status (keep full version)."""
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
            
            if not current_week:
                await update.message.reply_text("❌ No active week found.")
                return
            
            all_instances = (
                db.query(TaskInstance)
                .filter_by(week_id=current_week.id)
                .join(TaskType)
                .order_by(TaskType.category, TaskType.name)
                .all()
            )
            
            completed = [t for t in all_instances if t.status == "completed"]
            
            message = (
                f"📅 *Week {current_week.week_number}/{current_week.year}*\n"
                f"⏰ Deadline: {current_week.deadline.strftime('%A, %B %d at %H:%M')}\n\n"
            )
            
            # Progress by category
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
                message += f"{emoji} {category.title()}: {progress_bar} {stats['completed']}/{stats['total']}\n"
            
            # Overall progress
            total = sum([category_ammounts.get(cat, 1) for cat in by_category.keys()])
            completed_count = len(completed)
            if total > 0:
                progress = int((completed_count / total) * 10)
                progress_bar = "█" * progress + "░" * (10 - progress)
                message += f"\n📊 *Overall*: {progress_bar} {completed_count}/{total}\n\n"
            
            # Completed tasks (last 5)
            message += f"✅ *Completed ({completed_count})*\n"
            for task in completed[-5:]:
                completer = db.query(Person).get(task.completed_by)
                message += f"  • {task.task_type.name} - {completer.name}\n"
            if completed_count > 5:
                message += f"  ... and {completed_count - 5} more\n"
            
            # Check if done
            done = all(by_category[cat]["completed"] >= by_category[cat]["total"] for cat in by_category)
            if done:
                message += f"\n🎉 All tasks done! Time to relax! 😎🍹\n"
            
            # Non-contributors
            completed_by_ids = [t.completed_by for t in completed if t.completed_by]
            active_people = db.query(Person).filter_by(active=True).all()
            not_contributed = [p for p in active_people if p.id not in completed_by_ids]
            
            if not done and not_contributed:
                message += f"\n¿Y entonces qué? 😡🔪\n"
                message += f"💭 *Haven't contributed:* "
                message += ", ".join([p.name for p in not_contributed])
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all tasks."""
        with get_db() as db:
            tasks = db.query(TaskType).order_by(TaskType.category, TaskType.name).all()
            
            by_category = {}
            for task in tasks:
                category = task.category or "other"
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(task)
            
            message = "📋 *All Available Tasks*\n\n"
            
            for category, tasks in sorted(by_category.items()):
                emoji = category_emojis.get(category, "📦")
                target = category_ammounts.get(category, 1)
                message += f"{emoji} *{category.title()}* [Complete {target}/week]\n"
                for task in tasks:
                    duration = f" ({task.estimated_duration_minutes}min)" if task.estimated_duration_minutes else ""
                    message += f"  • {task.name}{duration}\n"
                message += "\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_my_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed personal stats."""
        user = update.effective_user
        
        with get_db() as db:
            person = db.query(Person).filter_by(telegram_id=user.id).first()
            if not person:
                await update.message.reply_text("❌ You're not registered! Use /start first.")
                return
            
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
                message = f"📊 *Stats for {person.name}*\n\nNo active week."
            
            all_time = db.query(TaskInstance).filter_by(completed_by=person.id).count()
            message += f"\n*All-Time:*\nTotal: *{all_time}* tasks\n"
            
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
        """Show corridor map."""
        media_path = project_root / "media" / "corridor-overview.jpg"
        
        if media_path.exists():
            with open(media_path, "rb") as img_file:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img_file,
                    caption="🗺️ *Corridor Map*",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text("❌ Map not found.")
    
    async def cmd_who_opted_out(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show opt-outs."""
        with get_db() as db:
            if not context.args:
                opt_outs = (
                    db.query(TaskOptOut)
                    .join(Person)
                    .join(TaskType)
                    .order_by(TaskType.category, TaskType.name)
                    .all()
                )
                
                if not opt_outs:
                    await update.message.reply_text("ℹ️ No opt-outs yet!")
                    return
                
                by_task = {}
                for opt_out in opt_outs:
                    task_name = opt_out.task_type.name
                    if task_name not in by_task:
                        by_task[task_name] = []
                    person = db.query(Person).get(opt_out.person_id)
                    by_task[task_name].append(f"{person.name} ({opt_out.reason})")
                
                message = "📋 *Current Opt-Outs*\n\n"
                for task_name in sorted(by_task.keys()):
                    message += f"*{task_name}:*\n"
                    for person_info in by_task[task_name]:
                        message += f"  • {person_info}\n"
                    message += "\n"
                
            else:
                task_query = " ".join(context.args)
                task_type = db.query(TaskType).filter(TaskType.name.ilike(f"%{task_query}%")).first()
                
                if not task_type:
                    await update.message.reply_text(f"❌ Task '{task_query}' not found.")
                    return
                
                opt_outs = db.query(TaskOptOut).filter_by(task_type_id=task_type.id).all()
                
                if not opt_outs:
                    message = f"ℹ️ No opt-outs for *{task_type.name}*"
                else:
                    message = f"📋 *Opt-Outs for {task_type.name}*\n\n"
                    for opt_out in opt_outs:
                        person = db.query(Person).get(opt_out.person_id)
                        message += f"• {person.name}\n  Reason: {opt_out.reason}\n\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Pablito's Corridor Manager Bot (Interactive Version)...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = CorridorBot()
    bot.run()
