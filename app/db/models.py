from sqlalchemy import ForeignKey, String, Text, Integer, Column
from sqlalchemy.orm import relationship


from .database import Base, TimestampMixin


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)

    tweets = relationship("Tweet", backref="author", cascade="all, delete-orphan")
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
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    media = relationship("Media", backref="tweet", cascade="all, delete-orphan")
    likes = relationship("Like", backref="tweet", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), primary_key=True)


class Follower(Base):
    __tablename__ = "followers"
    # user that follows
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    # are followed by user
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
