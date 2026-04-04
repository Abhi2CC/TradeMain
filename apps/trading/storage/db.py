from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from storage.models import Base

engine = create_engine(f'sqlite:///{settings.db_path}', future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
