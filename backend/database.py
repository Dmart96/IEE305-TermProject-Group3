from sqlmodel import SQLModel, create_engine

# SQLite DB file will live in the /database folder at project root
DATABASE_URL = "sqlite:///database/nps.db"

# Global engine object used by the app
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Create all tables in the database based on SQLModel models.
    Call once at startup.
    """
    from . import models  # ensures models are imported and tables registered
    SQLModel.metadata.create_all(engine)

