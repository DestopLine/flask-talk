from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_required, login_user
import flask_login
from sqlalchemy import select

from app.auth import setup_auth
from app.database import Session
from app.entities import Post, User, setup_db

flask_app = Flask(__name__)


def main() -> None:
    setup_db()
    setup_auth(flask_app, Session)
    flask_app.run(debug=True)


@flask_app.route("/")
def index():
    return redirect(url_for("home"))


@flask_app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username and password:
            with Session.begin() as session:
                user = session.scalars(
                    select(User)
                        .where(User.username == username and User.password == password)
                ).first()
                login_user(user)

            next = request.args.get("next")
            return redirect(next or url_for("index"))

        else:
            return "<h1>Intento de inicio de sesion fallido, intentar de nuevo</h1>"

    return render_template("login.html")


@flask_app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return "<h1>Las contraseñas no coinciden</h1>"

        with Session.begin() as session:
            existing_user = session.scalars(
                select(User).where(User.username == username)
            ).first()

            if existing_user is not None:
                return "<h1>El nombre de usuario especificado ya está en uso</h1>"

            new_user = User(username=username, password=password)
            session.add(new_user)
            session.flush()
            login_user(new_user)

        next = request.args.get("next")
        return redirect(next or url_for("home"))

    return render_template("registro.html")


@flask_app.route("/home")
@login_required
def home():
    with Session.begin() as session:
        stmt = select(Post)
        posts = session.scalars(stmt).all()
        return render_template("index.html", posts=posts)


@flask_app.route("/post", methods=["POST"])
@login_required
def post():
    pass


@flask_app.route("/logout", methods=["POST"])
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    main()
