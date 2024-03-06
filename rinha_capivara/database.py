import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rinha_capivara.settings import Settings

engine = create_engine(Settings().DATABASE_URL, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextlib.contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
