from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///base.db", echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

login_manager = LoginManager()
