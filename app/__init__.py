from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_required, login_user
from app.auth import setup_auth
from app.database import Session
from app.entities import User, setup_db, Post
from sqlalchemy import select

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


@flask_app.route("/home")
@login_required
def home():
    with Session.begin() as session:
        stmt = select(Post)
        posts = session.scalars(stmt).all()
    return render_template("index.html",posts=posts)

@flask_app.route("/post", methods=["POST"])
def post():
    pass

if __name__ == "__main__":
    main()
