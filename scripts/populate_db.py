"""Populate database with initial task types and test data."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
from src.database import get_db, init_db
from src.models import Person, TaskType, TaskOptOut, Week, TaskInstance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_task_types(db):
    """Create all task type definitions."""
    logger.info("Creating task types...")
    
    task_definitions = [
        # Toilets
        {
            "name": "Toilet 1",
            "category": "toilet",
            "description": "Clean toilet 1 (the closest to the main entrance)",
            "instructions": "1. Vacuum floor\n2. clean toilet bowl with toilet cleaner\n3. wipe sink, mirror & door handle\n4. mop floor\n5. empty trash bin\n6. refill toilet paper if needed",
            "estimated_duration_minutes": 45,
            "location": "Closest to main entrance, diagonally opposite kitchen"
        },
        {
            "name": "Toilet 2",
            "category": "toilet",
            "description": "Clean toilet 2 (the one next to toilet 1 with the john deer tractor poster)",
            "instructions": "1. Vacuum floor\n2. clean toilet bowl with toilet cleaner\n3. wipe sink, mirror & door handle\n4. mop floor\n5. empty trash bin\n6. refill toilet paper if needed",
            "estimated_duration_minutes": 45,
            "location": "Next to toilet 1, diagonally opposite kitchen"
        },
        {
            "name": "Toilet 3",
            "category": "toilet",
            "description": "Clean toilet 3 (aka ladies toilet)",
            "instructions": "1. Vacuum floor\n2. clean toilet bowl with toilet cleaner\n3. wipe sink, mirror & door handle\n4. mop floor\n5. empty trash bin\n6. refill toilet paper if needed",
            "estimated_duration_minutes": 45,
            "location": "Close to the end of the hall on the right side, after the laundry room."
        },
        {
            "name": "Toilet 4",
            "category": "toilet",
            "description": "Clean toilet 4 (male only toilet)",
            "instructions": "1. Vacuum floor\n2. clean toilet bowl with toilet cleaner\n3. wipe sink, mirror & door handle\n4. mop floor\n5. empty trash bin\n6. refill toilet paper if needed",
            "estimated_duration_minutes": 45,
            "location": "Right next to toilet 3, in the very end of the hall on the right side."
        },
        
        # Showers
        {
            "name": "Shower 1",
            "category": "shower",
            "description": "Clean shower room 1",
            "instructions": "1. Scrub shower walls and floor\n2. Clean drain\n3. Wipe mirrors and sinks\n4. Mop floor\n5. Empty trash",
            "estimated_duration_minutes": 60,
            "location": "Is the shower closest to the main entrance, diagonally opposite kitchen"
        },
        {
            "name": "Shower 2",
            "category": "shower",
            "description": "Clean shower room 2",
            "instructions": "1. Scrub shower walls and floor\n2. Clean drain\n3. Wipe mirrors and sinks\n4. Mop floor\n5. Empty trash",
            "estimated_duration_minutes": 60,
            "location": "Is the shower next to shower 1, diagonally opposite kitchen"
        },
        {
            "name": "Shower 3",
            "category": "shower",
            "description": "Clean shower room 3",
            "instructions": "1. Scrub shower walls and floor\n2. Clean drain\n3. Wipe mirrors and sinks\n4. Mop floor\n5. Empty trash",
            "estimated_duration_minutes": 60,
            "location": "On the right wing of the corridor, in the very end of the hall"
        },
        {
            "name": "Shower 4",
            "category": "shower",
            "description": "Clean shower room D",
            "instructions": "1. Scrub shower walls and floor\n2. Clean drain\n3. Wipe mirrors and sinks\n4. Mop floor\n5. Empty trash",
            "estimated_duration_minutes": 60,
            "location": "On the left wing of the corridor, in the very end of the hall"
        },
        
        # Kitchen
        {
            "name": "Kitchen A",
            "category": "kitchen",
            "description": "Clean stove, oven & extractor hood",
            "instructions": "Clean stove, oven & extractor hood. Wipe down surfaces.",
            "estimated_duration_minutes": 50,
            "location": "Main kitchen"
        },
        {
            "name": "Kitchen E",
            "category": "kitchen",
            "description": "Clean exterior surfaces",
            "instructions": "Clean floor, walls, table, outsides of cupboards/fridges, windows, couches (also behind couch). Deep-clean (behind) stove.",
            "estimated_duration_minutes": 45,
            "location": "Main kitchen"
        },
        {
            "name": "Kitchen I",
            "category": "kitchen",
            "description": "Clean interior and dishes",
            "instructions": "Clean insides of cupboards and microwave, sort dishes. Clean kitchen-block.",
            "estimated_duration_minutes": 35,
            "location": "Main kitchen"
        },
        
        # Fridges
        {
            "name": "Fridge 1",
            "category": "fridge",
            "description": "Clean communal fridge #1",
            "instructions": "Clean the fridge you use most. If that's in your room, you are 'Backup'.",
            "estimated_duration_minutes": 40,
            "location": "Look for the number on the fridge, as they are not in a particular order and they are subject to change in the future."
        },
        {
            "name": "Fridge 2",
            "category": "fridge",
            "description": "Clean communal fridge #2",
            "instructions": "Clean the fridge you use most. If that's in your room, you are 'Backup'.",
            "estimated_duration_minutes": 40,
            "location": "Look for the number on the fridge, as they are not in a particular order and they are subject to change in the future."
        },
        {
            "name": "Fridge 3",
            "category": "fridge",
            "description": "Clean communal fridge #3",
            "instructions": "Clean the fridge you use most. If that's in your room, you are 'Backup'.",
            "estimated_duration_minutes": 40,
            "location": "Look for the number on the fridge, as they are not in a particular order and they are subject to change in the future."
        },
        {
            "name": "Fridge 4",
            "category": "fridge",
            "description": "Clean communal fridge #4",
            "instructions": "Clean the fridge you use most. If that's in your room, you are 'Backup'.",
            "estimated_duration_minutes": 40,
            "location": "Look for the number on the fridge, as they are not in a particular order and they are subject to change in the future."
        },
        
        # Hallway/Common areas
        {
            "name": "Hall Cleaning",
            "category": "hallway",
            "description": "Vacuum and mop floor of the hall",
            "instructions": "Vacuum and mop the floor of Main hall and Side hall. Make pictures of stuff we don't use, remove if nobody claims/no need.",
            "estimated_duration_minutes": 40,
            "location": "Entire Hall"
        },
        
        # Laundry
        {
            "name": "Wash Room",
            "category": "laundry",
            "description": "Clean laundry room",
            "instructions": "Wash, hang and fold corridor wash. Deep-clean the machines and empty container.",
            "estimated_duration_minutes": 40,
            "location": "Laundry room"
        },
        
        # Trash
        {
            "name": "Trash Paper, Glass & Plastic",
            "category": "trash",
            "description": "Empty paper/cardboard, glass and plastic bins",
            "instructions": "Empty the paper/cardboard, glass and plastic bins to outside containers",
            "estimated_duration_minutes": 25,
            "location": "Kitchen"
        },
        {
            "name": "Trash Kitchen",
            "category": "trash",
            "description": "Empty kitchen trash",
            "instructions": "Empty the kitchen trash bin and clean the crates at the beginning of the hall",
            "estimated_duration_minutes": 15,
            "location": "Kitchen/Hall"
        },
    ]
    
    for task_def in task_definitions:
        task = TaskType(**task_def)
        db.add(task)
    
    db.commit()
    logger.info(f"Created {len(task_definitions)} task types")


def create_test_people(db):
    """Create test users for development."""
    logger.info("Creating test people...")
    
    # Create 3 test users (you can add real telegram IDs later)
    test_users = [
        {"telegram_id": 123456789, "name": "Alice", "username": "alice_test"},
        {"telegram_id": 987654321, "name": "Bob", "username": "bob_test"},
        {"telegram_id": 555555555, "name": "Charlie", "username": "charlie_test"},
    ]
    
    for user_data in test_users:
        person = Person(**user_data)
        db.add(person)
    
    db.commit()
    logger.info(f"Created {len(test_users)} test people")


def create_test_opt_outs(db):
    """Create some test opt-outs (people who don't use communal fridges, etc.)."""
    logger.info("Creating test opt-outs...")
    
    # Alice has her own fridge
    alice = db.query(Person).filter_by(name="Alice").first()
    fridges = db.query(TaskType).filter(TaskType.category == "fridge").all()
    
    for fridge in fridges:
        opt_out = TaskOptOut(
            person_id=alice.id,
            task_type_id=fridge.id,
            reason="Has own fridge in room"
        )
        db.add(opt_out)
    
    db.commit()
    logger.info("Created test opt-outs")


def create_current_week(db):
    """Create the current week with all task instances."""
    logger.info("Creating current week...")
    
    # Get current week number
    now = datetime.now()
    year, week_num, _ = now.isocalendar()
    
    # Calculate start date (Monday) and deadline (Friday 12:00)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    deadline = start_of_week + timedelta(days=4, hours=12)  # Friday 12:00
    
    # Create week
    week = Week(
        year=year,
        week_number=week_num,
        start_date=start_of_week.date(),
        deadline=deadline,
        closed=False
    )
    db.add(week)
    db.commit()
    
    # Get all task types and active people
    task_types = db.query(TaskType).all()
    people = db.query(Person).filter_by(active=True).all()
    
    # Create task instances (excluding opted-out combinations)
    created_count = 0
    for task_type in task_types:
        # Check if this is an optional task with opt-outs
        opt_out_person_ids = [
            opt.person_id 
            for opt in db.query(TaskOptOut).filter_by(task_type_id=task_type.id).all()
        ]
        
        # Always create the task instance (eligible people can claim it)
        instance = TaskInstance(
            week_id=week.id,
            task_type_id=task_type.id,
            status="pending"
        )
        db.add(instance)
        created_count += 1
    
    db.commit()
    logger.info(f"Created week {week_num}/{year} with {created_count} task instances")


def populate_database():
    """Main function to populate the database."""
    logger.info("Starting database population...")
    
    # Initialize database (create tables)
    init_db()
    
    with get_db() as db:
        # Check if data already exists
        if db.query(TaskType).count() > 0:
            logger.warning("Database already contains data. Skipping population.")
            logger.info("To reset, run: python scripts/reset_db.py")
            return
        
        # Create all data
        create_task_types(db)
        #create_test_people(db)
        #create_test_opt_outs(db)
        create_current_week(db)
    
    logger.info("Database population completed successfully!")
    logger.info("\nTest users created:")
    logger.info("  - Alice (telegram_id: 123456789) - opted out of fridges")
    logger.info("  - Bob (telegram_id: 987654321)")
    logger.info("  - Charlie (telegram_id: 555555555)")
    logger.info("\nYou can now start the bot and test with these users.")


if __name__ == "__main__":
    populate_database()