from flask import Flask, redirect, render_template, request, url_for

from app.entities import setup_db

flask_app = Flask(__name__)


def main() -> None:
    setup_db()
    flask_app.run(debug=True)


@flask_app.route("/")
def index():
    return render_template("index.html")


@flask_app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password:
            return redirect(url_for("index"))
        else:
            return "<h1>Intento de inicio de sesion fallido, intentar de nuevo</h1>"
    return render_template("login.html")


@flask_app.route("/post", methods=["POST"])
def create_post():
    return redirect(url_for("index"))


if __name__ == "__main__":
    main()
