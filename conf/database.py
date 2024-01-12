import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://root:nomelase@silicorn.ctmmjxlkwowe.us-west-2.rds.amazonaws.com:3306/silicorn"

engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)
