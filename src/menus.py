"""Menu creation functions for the Corridor Bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.database import get_db
from src.models import TaskType, TaskInstance, Week

# Category configuration
CATEGORY_AMOUNTS = {
    "toilet": 2,
    "shower": 2,
    "kitchen": 3,
    "fridge": 2,
    "hallway": 1,
    "laundry": 1,
    "trash": 2,
    "other": 1
}

CATEGORY_EMOJIS = {
    "toilet": "🚽",
    "shower": "🚿",
    "kitchen": "🍳",
    "fridge": "❄️",
    "hallway": "🚪",
    "laundry": "🧺",
    "trash": "🗑️",
    "other": "📦"
}

# NEW: Task frequency (how often each category needs to be done)
CATEGORY_FREQUENCY = {
    "toilet": 2,    # Every 2 weeks
    "shower": 2,    # Every 2 weeks
    "kitchen": 1,   # Every week (default)
    "fridge": 1,    # Every week
    "hallway": 1,   # Every week
    "laundry": 1,   # Every week
    "trash": 1,     # Every week
    "other": 1      # Every week
}


def create_main_menu(is_private: bool = True) -> InlineKeyboardMarkup:
    """Create the main menu keyboard based on chat type."""
    if is_private:
        # Full menu for private chat
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
    else:
        # Limited menu for group chat (only public actions)
        keyboard = [
            [
                InlineKeyboardButton("📋 View Status", callback_data="status"),
                InlineKeyboardButton("📝 List Tasks", callback_data="tasks")
            ],
            [
                InlineKeyboardButton("👥 Who Opted Out", callback_data="whooptedout"),
                InlineKeyboardButton("💡 Help", callback_data="help")
            ]
        ]
    
    return InlineKeyboardMarkup(keyboard)


def create_category_menu(action: str = "complete") -> InlineKeyboardMarkup:
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
            
            emoji = CATEGORY_EMOJIS.get(category, "📦")
            stats = by_category[category]
            button_text = f"{emoji} {category.title()} ({stats['completed']}/{CATEGORY_AMOUNTS.get(category, 1)})"
            
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

def create_task_menu(category: str, action: str = "complete") -> InlineKeyboardMarkup:
    """Create task selection menu for a category."""
    with get_db() as db:
        current_week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
        
        if not current_week:
            return None
        
        # Get category frequency
        frequency = CATEGORY_FREQUENCY.get(category, 1)
        
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
        
        tasks = query.order_by(TaskType.name).all()
        
        if not tasks:
            return None
        
        # Filter tasks by frequency (only for complete action)
        if action == "complete" and frequency > 1:
            # Get recent weeks to check
            recent_weeks = (
                db.query(Week)
                .filter(Week.closed == True)
                .order_by(Week.deadline.desc())
                .limit(frequency - 1)
                .all()
            )
            recent_week_ids = [w.id for w in recent_weeks]
            
            # Filter out tasks completed recently
            filtered_tasks = []
            for task in tasks:
                # Check if this task type was completed in recent weeks
                was_completed_recently = (
                    db.query(TaskInstance)
                    .filter(
                        TaskInstance.task_type_id == task.task_type_id,
                        TaskInstance.week_id.in_(recent_week_ids),
                        TaskInstance.status == "completed"
                    )
                    .first()
                )
                
                if not was_completed_recently:
                    filtered_tasks.append(task)
            
            tasks = filtered_tasks
        
        if not tasks:
            return None
        
        # Create buttons
        keyboard = []
        for task in tasks:
            task_type = task.task_type
            duration = f" - {task_type.estimated_duration_minutes}min" if task_type.estimated_duration_minutes else ""
            status_emoji = "✅" if task.status == "completed" else "⏳"
            button_text = f"{status_emoji} {task_type.name}{duration}"
            
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"{action}:task:{task.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Categories", callback_data=f"{action}:categories")])
        
        return InlineKeyboardMarkup(keyboard)
