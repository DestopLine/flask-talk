from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, LargeBinary, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, db


def setup_db() -> None:
    Base.metadata.create_all(db)


# Tablas intermedias
followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True),
    Column("following_id", ForeignKey("users.id"), primary_key=True),
)

post_likes_table = Table(
    "post_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
)

comment_likes_table = Table(
    "comment_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("comment_id", ForeignKey("comments.id"), primary_key=True),
)

reply_likes_table = Table(
    "reply_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("reply_id", ForeignKey("replies.id"), primary_key=True),
)


# Modelos
class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    displayname: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    password: Mapped[str]
    avatar: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    followers: Mapped[list["User"]] = relationship(
        secondary=followers_table,
        primaryjoin=id == followers_table.c.following_id,
        secondaryjoin=id == followers_table.c.follower_id,
        overlaps="following, users",
    )
    following: Mapped[list["User"]] = relationship(
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.following_id,
        overlaps="followers, users",
    )
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    replies: Mapped[list["Reply"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={repr(self.username)})"

    def get_id(self) -> str:
        return str(self.id)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="posts")
    likes: Mapped[list[User]] = relationship(secondary=post_likes_table)
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    post: Mapped[Post] = relationship(back_populates="comments")
    user: Mapped[User] = relationship(back_populates="comments")
    replies: Mapped[list["Reply"]] = relationship(back_populates="comment")
    likes: Mapped[list[User]] = relationship(secondary=comment_likes_table)


class Reply(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    comment: Mapped[Comment] = relationship(back_populates="replies")
    user: Mapped[User] = relationship(back_populates="replies")
    likes: Mapped[list[User]] = relationship(secondary=reply_likes_table)
