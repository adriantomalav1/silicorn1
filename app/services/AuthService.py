from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.exceptions.HttpExceptions import InvalidCredentialsException

from conf.config import AUTH_ALGORITHM, AUTH_SECRET_KEY, oauth2_scheme

from app.models.UserModel import UserModel
from app.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class AuthService:
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def get_hashed_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def register(username: str, password: str) -> str:
        user = UserModel().get_user(username)
        if user:
            raise HTTPException(status_code=401)
        hashed_password = pwd_context.hash(password)
        UserModel().create_user(username, hashed_password)
        return username

    @staticmethod
    def login(username: str, password: str) -> str:
        user = UserModel().get_user(username)
        if not user:
            raise HTTPException(status_code=401)
        if not AuthService.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401)
        return AuthService.get_access_token(user)

    @staticmethod
    def get_access_token(user: User) -> bool:
        access_token_expires = timedelta(hours=48)
        return AuthService.create_token({"sub": user.username}, access_token_expires)

    @staticmethod
    def create_token(data: dict, time_expire: datetime) -> bool:
        data_copy = data.copy()
        expires = datetime.utcnow() + time_expire
        data_copy.update({"exp": expires})
        return jwt.encode(data_copy, key=AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        try:
            username = jwt.decode(token, key=AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM]).get("sub")
            if username is None:
                raise InvalidCredentialsException()
        except JWTError:
            raise InvalidCredentialsException()

        user = UserModel().get_user(username)

        if not user:
            raise InvalidCredentialsException()

        return user
