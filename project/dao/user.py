from typing import Union

from sqlalchemy.exc import NoResultFound

from .models import User
from .base import BaseDAO


class UserDAO(BaseDAO):

    def get_by_email(self, email: str) -> Union[User, None]:
        """
        Получить пользователя по имейлу
        """
        try:
            user = self.session.query(User).filter(User.email == email).one()
            return user
        except NoResultFound:
            return None

    def create(self, data: dict) -> User:
        """Создать пользователя в БД"""
        user = User(**data)
        self.session.add(user)
        self.session.commit()
        return user

    def update_by_email(self, data: dict, email: str) -> None:
        """Обновить пользователя по его имейлу"""
        self.session.query(User).filter(User.email == email).update(data)
        self.session.commit()
