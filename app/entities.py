from datetime import datetime
from typing import Optional

from flask import url_for
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, LargeBinary, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, db


def setup_db() -> None:
    # Crea todas las tablas en la base de datos
    Base.metadata.create_all(db)


# Tablas intermedias para relaciones muchos a muchos
# Usadas para gestionar las relaciones de seguidores, likes en posts, comentarios y respuestas
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


# Modelo de Usuario
class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)  # Nombre de usuario único
    displayname: Mapped[Optional[str]]  # Nombre de visualización opcional
    bio: Mapped[Optional[str]]  # Biografía opcional
    password: Mapped[str]  # Contraseña del usuario
    avatar: Mapped[Optional[bytes]] = mapped_column(LargeBinary)  # Avatar del usuario (almacenado como binario)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # Fecha de creación

    # Relación de seguidores (usuarios que siguen a este usuario)
    followers: Mapped[list["User"]] = relationship(
        secondary=followers_table,
        primaryjoin=id == followers_table.c.following_id,
        secondaryjoin=id == followers_table.c.follower_id,
        overlaps="following, users",
    )
    
    # Relación de usuarios a los que sigue
    following: Mapped[list["User"]] = relationship(
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.following_id,
        overlaps="followers, users",
    )
    
    # Relación con los posts, comentarios y respuestas del usuario
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    replies: Mapped[list["Reply"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        # Representación del usuario
        return f"User(id={self.id}, username={repr(self.username)})"

    def get_id(self) -> str:
        # Retorna el ID del usuario como string
        return str(self.id)

    @property
    def avatar_url(self) -> str:
        # Genera la URL del avatar del usuario
        return url_for("avatar", id=self.id)


# Modelo de Post
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Relación con el usuario que crea el post
    text: Mapped[str]  # Contenido del post
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)  # Imagen del post (opcional)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # Fecha de creación
    edited_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())  # Fecha de edición (si se edita)

    user: Mapped[User] = relationship(back_populates="posts")  # Relación con el usuario creador del post
    likes: Mapped[list[User]] = relationship(secondary=post_likes_table)  # Relación de likes
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete")  # Relación con comentarios

    @property
    def image_url(self) -> str:
        # Genera la URL de la imagen del post
        return url_for("post_image", post_id=self.id)


# Modelo de Comment
class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))  # Relación con el post al que pertenece el comentario
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Relación con el usuario que hace el comentario
    text: Mapped[str]  # Contenido del comentario
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # Fecha de creación

    post: Mapped[Post] = relationship(back_populates="comments")  # Relación con el post
    user: Mapped[User] = relationship(back_populates="comments")  # Relación con el usuario
    replies: Mapped[list["Reply"]] = relationship(back_populates="comment", cascade="all, delete")  # Respuestas al comentario
    likes: Mapped[list[User]] = relationship(secondary=comment_likes_table)  # Relación de likes en el comentario


# Modelo de Reply
class Reply(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))  # Relación con el comentario al que responde
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Relación con el usuario que hace la respuesta
    text: Mapped[str]  # Contenido de la respuesta
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # Fecha de creación

    comment: Mapped[Comment] = relationship(back_populates="replies")  # Relación con el comentario
    user: Mapped[User] = relationship(back_populates="replies")  # Relación con el usuario
    likes: Mapped[list[User]] = relationship(secondary=reply_likes_table)  # Relación de likes en la respuesta
