"""
UATMMS Database Session Management (Phase 8)
Database engine, session factory, and dependency injection.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from backend.app.core.logging import logger

# ============================================================================
# Database Configuration
# ============================================================================

# PostgreSQL connection string from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://uatmms_user:uatmms_pass@localhost:5432/uatmms_db"
)

# Connection pool settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # Recycle connections after 1 hour

# ============================================================================
# Engine & Session Factory
# ============================================================================

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if os.getenv("DB_USE_NULL_POOL") == "true" else None,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    echo=False,  # Set to True for SQL logging
    connect_args={
        "connect_timeout": 10,
        "application_name": "uatmms",
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================================
# Dependency Injection
# ============================================================================

def get_db() -> Session:
    """
    FastAPI dependency for database session.
    Yields a session and ensures cleanup after request.
    
    Usage in endpoint:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Connection Verification
# ============================================================================

def verify_database_connection() -> bool:
    """
    Verify that database connection is working.
    Called during application startup.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified ✓")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ============================================================================
# Initialization
# ============================================================================

def init_db():
    """
    Initialize database on application startup.
    Creates all tables if they don't exist.
    """
    from backend.app.db.models import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized ✓")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def close_db():
    """
    Close database connections on application shutdown.
    """
    engine.dispose()
    logger.info("Database connections closed ✓")
