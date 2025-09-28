"""
ORM-модели приложения: User, Tweet, Media, Like, Follower.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base, TimestampMixin


class User(Base):
    """
    Модель пользователя.

    Пользователь может создавать твиты, ставить лайки, иметь подписчиков.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)

    tweets = relationship(
        "Tweet", backref="author", cascade="all, delete-orphan"
    )
    likes = relationship("Like", backref="user", cascade="all, delete-orphan")
    followers = relationship(
        "Follower",
        foreign_keys="Follower.following_id",
        backref="following",
        cascade="all, delete-orphan",
    )
    following = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        backref="follower",
        cascade="all, delete-orphan",
    )


class Tweet(Base, TimestampMixin):
    """
    Модель твита.

    Твит содержит текст, ссылку на автора, медиа и лайки.
    """

    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    media = relationship(
        "Media", backref="tweet", cascade="all, delete-orphan"
    )
    likes = relationship("Like", backref="tweet", cascade="all, delete-orphan")


class Media(Base):
    """
    Модель медиафайла (например, изображения).

    Связана с твитом через внешний ключ.
    """

    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)


class Like(Base):
    """
    Модель лайка.

    Составной первичный ключ: (user_id, tweet_id).
    """

    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), primary_key=True)


class Follower(Base):
    """
    Модель подписки.

    Составной первичный ключ: (follower_id, following_id).
    """

    __tablename__ = "followers"
    # Пользователь, который подписывается
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    # Пользователь, на которого подписываются
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
