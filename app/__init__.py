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
                    .where((User.username == username) & (User.password == password))
                    ).first()
                login_user(user)
                if user:
                    login_user(user)
                    next = request.args.get("next")
                    return redirect(next or url_for("home"))
                else:
                    return "<h1>Intento de inicio de sesión fallido. Intenta de nuevo.</h1>"
    return render_template("login.html")


@flask_app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmar_password = request.form["confirmar_password"]
        if password != confirmar_password:
            return "<h1>Las contraseñas no coinciden</h1>"
        elif password == confirmar_password:
            with Session.begin() as session:
                user = session.scalars(
                    select(User)
                    .where((User.username == username) & (User.password == confirmar_password))
                ).first
                login_user(user)
                if user:
                    login_user(user)
                    next = request.args.get("next")
                    return redirect(next or url_for("home"))
                else:
                    return "<h1>Intento de inicio de sesion fallido. Intenta de nuevo</h1>"
    return render_template("registro.html")

@flask_app.route("/home")
@login_required
def home():
    with Session.begin() as session:
        stmt = select(Post)
        posts = session.scalars(stmt).all()
    return render_template("index.html",posts=posts)

@flask_app.route("/post", methods=["POST"])
@login_required
def post():
    pass

if __name__ == "__main__":
    main()
