import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
try:
    from alembic import context
except ImportError:
    context = None

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL and context is not None:
    try:
        alembic_cfg_url = context.config.get_main_option("sqlalchemy.url")
        make_url(alembic_cfg_url)
        SQLALCHEMY_DATABASE_URL = alembic_cfg_url
    except Exception:
        pass

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()