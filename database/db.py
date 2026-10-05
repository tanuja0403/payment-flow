from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLite database URL
DATABASE_URL = "sqlite:///./payflow.db"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
Base = declarative_base()


# Create a database session
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()