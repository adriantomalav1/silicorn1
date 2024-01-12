import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "awseb-e-vpfvgasupm-stack-awsebrdsdatabase-rsjv6gqxv7xb.ctmmjxlkwowe.us-west-2.rds.amazonaws.com:3306/silicorn"

engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)
