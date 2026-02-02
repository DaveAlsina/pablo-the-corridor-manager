"""Reset the database (drop and recreate all tables)."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import drop_db, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """Drop and recreate all tables."""
    logger.warning("=" * 60)
    logger.warning("WARNING: This will delete ALL data in the database!")
    logger.warning("=" * 60)
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        logger.info("Reset cancelled.")
        return
    
    logger.info("Dropping all tables...")
    drop_db()
    
    logger.info("Creating fresh tables...")
    init_db()
    
    logger.info("Database reset complete!")
    logger.info("Run 'python scripts/populate_db.py' to add initial data.")


if __name__ == "__main__":
    reset_database()