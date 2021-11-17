#!/usr/bin/env python3
"""Auth module"""
import bcrypt
import uuid
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from user import User


def _hash_password(password: str) -> str:
    """Return bytes hashed with bcrypt.hashpw"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Return a string representation of a new UUID."""
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database."""

    def __init__(self):
        """Constructor"""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register new user with the database"""
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            password = _hash_password(password)
            user = self._db.add_user(email, password)
            return user
        raise ValueError('User {} already exists'.format(user.email))

    def valid_login(self, email: str, password: str) -> bool:
        """Checks if email and password match"""
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)

    def create_session(self, email: str) -> str:
        """Find user, generate and return id session"""
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        user.session_id = _generate_uuid()
        return user.session_id

    def get_user_from_session_id(self, session_id: str) -> User:
        """Return User by session ID"""
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """Delete user’s session ID"""
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return None
        user.session_id = None
