from flask import Flask
from flask_login import LoginManager
from sqlalchemy.orm import Session, sessionmaker

from app.entities import User


def setup_auth(app: Flask, DbSession: sessionmaker[Session]) -> None:
    login_manager = LoginManager()
    login_manager.init_app(app)
    app.secret_key = "7297c79d0268931ab71a1e9c12ab6daf40c8c18e639fabce8924b5d079aeb108"

    def load_user(user_id: str) -> User | None:
        with DbSession.begin() as session:
            session.expire_on_commit = False
            return session.query(User).where(User.id == user_id).first()

    login_manager.user_loader(load_user)
    login_manager.login_view = "login"  # type: ignore
