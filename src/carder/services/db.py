from pathlib import Path
from sqlalchemy import create_engine
import sqlalchemy.orm as sa_orm

from carder.models import db as db_model

SQLITE_DB = Path("./state/cards.db")
CONNECTION_STRING = f"sqlite:///{SQLITE_DB}"

Engine = create_engine(CONNECTION_STRING)
Session = sa_orm.sessionmaker(bind=Engine)


def init_db():
    db_model.Base.metadata.create_all(Engine)
