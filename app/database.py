import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker

db = sa.create_engine("sqlite:///flask-chat.db", echo=True)
Session = sessionmaker(bind=db)
Base = declarative_base()
