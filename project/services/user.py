import base64
import hashlib
import hmac

from flask import current_app
from werkzeug.exceptions import MethodNotAllowed

from project.dao.models import User
from project.exceptions import UserAlreadyExists, IncorrectPassword, ItemNotFound
from project.services.base import BaseService


class UserService(BaseService):

    def get_by_email(self, email: str) -> User:
        """
        Получить дату пользователя по его почте
        """
        user = self.dao.get_by_email(email)
        if not user:
            raise ItemNotFound
        return user

    def create(self, data: dict) -> User:
        """Добавить пользователя"""
        # Check if user already exists
        user = self.dao.get_by_email(data.get('email'))
        if user:
            raise UserAlreadyExists

        # Hash password and add user to the database
        data['password'] = self.hash_password(data.get('password'))
        user = self.dao.create(data)
        return user

    def update_info(self, data: dict, email: str) -> None:
        """
        Обновить пользователя
        """
        # Check user exists
        self.get_by_email(email)
        # Check data is okay
        if 'password' not in data.keys() and 'email' not in data.keys():
            self.dao.update_by_email(data, email)
        else:
            raise MethodNotAllowed

    def update_password(self, data: dict, email: str) -> None:
        """
        Обновить пароль пользователя
        """

        # Check data is okay
        user = self.get_by_email(email)
        current_password = data.get('old_password')
        new_password = data.get('new_password')

        if None in [current_password, new_password]:
            raise MethodNotAllowed

        if not self.compare_passwords(user.password, current_password):
            raise IncorrectPassword

        # Hash password and update
        data = {
            'password': self.hash_password(new_password)
        }
        self.dao.update_by_email(data, email)

    def hash_password(self, password: str) -> bytes:
        """Хэширует пароль"""
        hash_digest = self.create_hash(password)
        encoded_digest = base64.b64encode(hash_digest)
        return encoded_digest

    def create_hash(self, password: str) -> bytes:
        """Генератор хэша"""
        hash_digest: bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            current_app.config.get('PWD_HASH_SALT'),
            current_app.config.get('PWD_HASH_ITERATIONS')
        )
        return hash_digest

    def compare_passwords(self, password_hash: str, password_passed: str) -> bool:
        """Сравнить введенный пароль и пароль из БД"""
        # Make passwords comparable
        decoded_digest: bytes = base64.b64decode(password_hash)
        passed_hash: bytes = self.create_hash(password_passed)
        # Compare
        is_equal = hmac.compare_digest(decoded_digest, passed_hash)
        return is_equal
