from io import BytesIO
import flask_login
from flask import Flask, flash, abort, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import select
from app.auth import setup_auth
from app.database import Session
from app.entities import Post, User, Comment, Reply, followers_table, setup_db

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
    with Session.begin() as session:
        user = session.get(User, current_user.id)

        if user is None:
            return "<h1>Usuario no encontrado</h1>", 404

        try:
            image = request.files["image"] or None
            new_post = Post(
                user_id=user.id,
                text=request.form["content"],
            )
            if image is not None:
                new_post.image = image.stream.read()
        except KeyError:
            return "Json mal formado", 400

        session.add(new_post)

    return redirect(url_for("home"))


@flask_app.route("/post/<int:post_id>/image")
def post_image(post_id: int):
    with Session.begin() as session:
        post = session.get(Post, post_id)

        if post is None:
            return "Post not found", 404

        if post.image is None:
            return "Image not found", 404

        return send_file(BytesIO(post.image), mimetype="image/gif")


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


@flask_app.route("/seguir/<int:user_id>", methods=["POST"])
@login_required
def seguir(user_id):
    with Session.begin() as session:
        # Obtener al usuario que se quiere seguir
        user_to_follow = session.get(User, user_id)
        if user_to_follow is None:  # Validar si el usuario existe
            abort(404, description="Usuario no encontrado")

        # Verificar que el usuario no se siga a sí mismo
        if user_to_follow.id == current_user.id:
            abort(400, description="No puedes seguirte a ti mismo")

        # Añadir la relación de seguimiento
        current_user_db = session.merge(current_user)  # Actualizar el usuario actual en la sesión
        if user_to_follow not in current_user_db.following:
            current_user_db.following.append(user_to_follow)
            session.commit()

    return redirect(url_for("perfil", user_id=user_id))


@flask_app.route("/dejar_de_seguir/<int:user_id>", methods=["POST"])
@login_required
def dejar_de_seguir(user_id):
    with Session.begin() as session:
        # Obtener al usuario que se quiere dejar de seguir
        user_to_unfollow = session.get(User, user_id)
        if user_to_unfollow is None:  # Validar si el usuario existe
            abort(404, description="Usuario no encontrado")

        # Verificar que el usuario no se deje de seguir a sí mismo
        if user_to_unfollow.id == current_user.id:
            abort(400, description="No puedes dejar de seguirte a ti mismo")

        # Remover la relación de seguimiento
        current_user_db = session.merge(current_user)  # Actualizar el usuario actual en la sesión
        if user_to_unfollow in current_user_db.following:
            current_user_db.following.remove(user_to_unfollow)
            session.commit()

    return redirect(url_for("perfil", user_id=user_id))


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
            return redirect(url_for('publicaciones', post_id=post.id))

        # Cargar comentarios junto con sus respuestas y usuarios asociados
        comments = session.query(Comment).filter_by(post_id=post.id).all()
        for comment in comments:
            session.refresh(comment, ["replies", "user"])  # Asegúrate de cargar las respuestas y usuarios

        return render_template('publicaciones.html', post=post, comments=comments)


@flask_app.route("/post/<int:post_id>", methods=["DELETE"])
@login_required
def eliminar_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)

        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        if current_user.id != post.user.id:
            return "Solo el usuario que publicó el post puede eliminarlo", 403

        session.delete(post)
        return "Post eliminado", 200


@flask_app.route("/post/<int:post_id>", methods=["PUT"])
@login_required
def editar_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)

        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        if current_user.id != post.user.id:
            return "Solo el usuario que publicó el post puede eliminarlo", 403

        try:
            body = request.json
            if body is None:
                raise KeyError
            post.text = body["text"]
        except KeyError:
            return "Json inválido", 400

        return "Post editado exitosamente", 200


@flask_app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def likes_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)
        user = session.get(User, current_user.id)

        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        if user in post.likes:
            post.likes.remove(user)
            return {
                "liked": False,
                "likes": len(post.likes),
            }, 200
        else:
            post.likes.append(user)
            return {
                "liked": True,
                "likes": len(post.likes),
            }, 200


@flask_app.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def Comentarios_likes(comment_id):
    with Session.begin() as session:
        comment = session.get(Comment, comment_id)
        if not comment:
            return "<h1>No hay comentarios</h1>"
        if current_user in comment.likes:
            comment.likes.remove(current_user)
        else:
            comment.likes.append(current_user)
        return redirect(url_for("publicaciones", post_id=comment.post_id))


@flask_app.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def responder_comentario(comment_id):
    with Session.begin() as session:
        comentario = session.get(Comment, comment_id)
        if not comentario:
            return "<h1>El comentario no existe</h1>", 404

        texto_respuesta = request.form.get('response')
        if not texto_respuesta or texto_respuesta.strip() == "":
            return "<h1>El texto de la respuesta no puede estar vacío</h1>", 400

        nueva_respuesta = Reply(
            comment_id=comment_id,
            user_id=current_user.id,
            text=texto_respuesta.strip()
        )
        session.add(nueva_respuesta)
        return redirect(url_for('publicaciones', post_id=comentario.post_id))


@flask_app.route("/logout", methods=["POST"])
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


@flask_app.route("/avatar/<int:id>")
def avatar(id: int):
    with Session.begin() as session:
        user = session.get(User, id)

        if user is None:
            return "User not found", 404

        if user.avatar is None:
            return send_file("static/images/default_avatar.png", mimetype="image/gif")

        return send_file(BytesIO(user.avatar), mimetype="image/gif")


@flask_app.route("/preferencias", methods=["GET", "POST"])
@login_required
def preferencias():
    if request.method == "GET":
        return render_template("preferencias.html")

    with Session.begin() as session:
        user = session.get(User, current_user.id)
        assert user is not None

        user.displayname = request.form["displayname"] or None
        user.bio = request.form["bio"] or None

        avatar_file = request.files["avatar"] or None
        if avatar_file is not None:
            user.avatar = avatar_file.stream.read()

    return "<h1>Cambios guardados exitosamente</h1>"


if __name__ == "__main__":
    main()
