"""
Database Setup Script
Creates all tables for SQLite/PostgreSQL
"""
from app.db.database import sync_engine
from app.db.models.models import Base
from app.core.logging import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)

def setup_database():
    """Create all tables"""
    log.info("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    log.info("✅ Database setup complete!")

if __name__ == "__main__":
    setup_database()
