from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass

# from potato_pyserver.config import settings
# SQLALCHEMY_DATABASE_URL = settings.database_url

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

POSTGRES_URL = "postgresql+psycopg://postgres:example@localhost/postgres"

engine = create_engine(POSTGRES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
