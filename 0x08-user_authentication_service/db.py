#!/usr/bin/env python3
"""DB module"""
from sqlalchemy import create_engine, update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from user import Base, User


class DB:
    """DB class"""

    def __init__(self) -> None:
        """Initialize a new DB instance"""

        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object"""

        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Save user to the database"""

        newUser = User(email=email, hashed_password=hashed_password)
        self._session.add(newUser)
        self._session.commit()
        return newUser

    def find_user_by(self, **kwargs) -> User:
        """Returns the first row found in the users table"""

        if not kwargs:
            raise InvalidRequestError

        # print("Found user: kwargs: ", kwargs)
        user = self._session.query(User).filter_by(**kwargs).first()
        # users = self._session.query(User).all()
        # print("Found user: users: ", users)

        if user is None:
            raise NoResultFound
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update the user’s attributes"""

        user = self.find_user_by(id=user_id)
        attr = list(kwargs)
        if attr[0] in dir(user):
            updatedUser = (update(User)
                           .where(User.id == user_id)
                           .values(**kwargs))
            self._session.execute(updatedUser)
            self._session.commit()
        else:
            raise ValueError
