"""Test script to verify database and configuration setup."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.database import get_db
from src.models import Person, TaskType, Week, TaskInstance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test if configuration is loaded correctly."""
    logger.info("Testing configuration...")
    
    try:
        assert settings.telegram_bot_token, "TELEGRAM_BOT_TOKEN not set"
        assert settings.telegram_chat_id, "TELEGRAM_CHAT_ID not set"
        assert settings.postgres_password, "POSTGRES_PASSWORD not set"
        logger.info("✅ Configuration loaded successfully")
        logger.info(f"   Database: {settings.postgres_db}")
        logger.info(f"   Host: {settings.postgres_host}:{settings.postgres_port}")
        return True
    except AssertionError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("   Please check your .env file")
        return False


def test_database_connection():
    """Test if database connection works."""
    logger.info("Testing database connection...")
    
    try:
        with get_db() as db:
            # Simple query to test connection
            result = db.execute("SELECT 1").scalar()
            assert result == 1
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("   Ensure PostgreSQL is running: docker-compose up -d")
        return False


def test_database_tables():
    """Test if all tables exist and have data."""
    logger.info("Testing database tables...")
    
    try:
        with get_db() as db:
            # Check if tables exist by counting records
            task_types = db.query(TaskType).count()
            people = db.query(Person).count()
            weeks = db.query(Week).count()
            
            logger.info(f"   Task types: {task_types}")
            logger.info(f"   People: {people}")
            logger.info(f"   Weeks: {weeks}")
            
            if task_types == 0:
                logger.warning("⚠️  No task types found. Run: python scripts/populate_db.py")
                return False
            
            if weeks == 0:
                logger.warning("⚠️  No weeks found. Run: python scripts/populate_db.py")
                return False
            
            logger.info("✅ Database tables populated")
            return True
    except Exception as e:
        logger.error(f"❌ Database table check failed: {e}")
        logger.error("   Tables might not exist. Run: python scripts/populate_db.py")
        return False


def test_current_week():
    """Test if current week exists and has tasks."""
    logger.info("Testing current week setup...")
    
    try:
        with get_db() as db:
            current_week = db.query(Week).filter_by(closed=False).first()
            
            if not current_week:
                logger.warning("⚠️  No active week found")
                return False
            
            task_instances = db.query(TaskInstance).filter_by(week_id=current_week.id).count()
            
            logger.info(f"   Week: {current_week.week_number}/{current_week.year}")
            logger.info(f"   Deadline: {current_week.deadline}")
            logger.info(f"   Task instances: {task_instances}")
            
            if task_instances == 0:
                logger.warning("⚠️  No task instances for current week")
                return False
            
            logger.info("✅ Current week configured correctly")
            return True
    except Exception as e:
        logger.error(f"❌ Current week check failed: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    logger.info("=" * 60)
    logger.info("Corridor Bot - Setup Verification")
    logger.info("=" * 60)
    
    results = {
        "Configuration": test_configuration(),
        "Database Connection": test_database_connection(),
        "Database Tables": test_database_tables(),
        "Current Week": test_current_week(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary:")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("🎉 All tests passed! You're ready to run the bot.")
        logger.info("   Start with: python src/bot.py")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above.")
        logger.error("   Common fixes:")
        logger.error("   1. Check your .env file exists and is configured")
        logger.error("   2. Start PostgreSQL: docker-compose up -d")
        logger.error("   3. Populate database: python scripts/populate_db.py")
    logger.info("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())