from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)
