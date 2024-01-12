from typing import Union
from sqlalchemy import create_engine
from conf.database import session_maker
from app.models.models import User


class UserModel:

    @staticmethod
    def get_user(username) -> Union[User, None]:
        session = session_maker()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        return user

    @staticmethod
    def create_user(email: str, hashed_password: str) -> User:
        new_user = User(
            username = email,
            email = email,
            hashed_password = hashed_password,
        )

        session = session_maker()
        session.add(new_user)
        session.commit()

        user = new_user
        session.close()

        return user
