from io import BytesIO
import flask_login
from flask import Flask, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import select
from app.auth import setup_auth
from app.database import Session
from app.entities import Post, User, Comment, setup_db

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
                user = (
                    session
                    .query(User)
                    .where(User.username == username and User.password == password)
                    .first()
                )

                if user is None:
                    return "<h1>Usuario o contraseña incorrectos</h1>"

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
            existing_user = (
                session
                .query(User)
                .where(User.username == username)
                .first()
            )

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
        # Asegúrate de que current_user esté cargado completamente
        user = session.merge(current_user)
        # Obtén las publicaciones
        posts = session.query(Post).order_by(Post.created_at.desc()).all()
        return render_template("index.html", current_user=user, posts=posts)


@flask_app.route("/post", methods=["POST"])
@login_required
def post():
    content = request.form["content"]  # Asegúrate de capturar el contenido del post
    with Session.begin() as session:
        # Recargar al usuario desde la base de datos
        user = session.get(User, current_user.id)

        if user is None:
            return "<h1>Usuario no encontrado</h1>", 404

        # Crear y guardar el nuevo post
        new_post = Post(user_id=user.id, text=content)
        session.add(new_post)  # Usar session en lugar de db.session
        session.commit()  # Usar session.commit()

    return redirect(url_for("home"))

@flask_app.route("/perfil/<int:user_id>", methods=["GET"])
@login_required
def perfil(user_id):
    with Session.begin() as session:
        user = session.get(User, user_id)
        if not user:
            return "<h1>Usuario no encontrado</h1>", 404

        # Cargar las publicaciones del usuario
        user_posts = session.scalars(
            select(Post).where(Post.user_id == user_id).order_by(Post.created_at.desc())
        ).all()

        # Pasar un nuevo objeto user completamente gestionado por la sesión activa
        return render_template("perfil.html", user=user, posts=user_posts)


@flask_app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def publicaciones(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)
        if not post:
            return "<h1>Publicación no encontrada</h1>", 404
        if request.method == 'POST':
            comment_text = request.form['comment']
            new_comment = Comment(text=comment_text, user_id=current_user.id, post_id=post.id)
            session.add(new_comment)
            session.commit()
            return redirect(url_for('publicaciones', post_id=post.id))
        comments = session.query(Comment).filter_by(post_id=post.id).all()
        return render_template('publicaciones.html', post=post, comments=comments)


@flask_app.route("/logout", methods=["POST"])
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


@flask_app.route("/avatar/<id>")
def avatar(id: int):
    with Session.begin() as session:
        user = session.get(User, id)

        if user is None:
            return "User not found", 404

        if user.avatar is None:
            return send_file("static/images/default_avatar.png", mimetype="image/gif")

        return send_file(BytesIO(user.avatar), mimetype="image/gif")


if __name__ == "__main__":
    main()
