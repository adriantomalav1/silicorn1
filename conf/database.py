import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://root@localhost:3316/silicorn"

engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)
