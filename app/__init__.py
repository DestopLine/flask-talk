from io import BytesIO

from flask import Flask, abort, redirect, render_template, request, send_file, url_for
import flask_login
from flask_login import current_user, login_required, login_user
from sqlalchemy import select

from app.auth import setup_auth
from app.database import Session
from app.entities import Comment, Post, Reply, User, followers_table, setup_db

# Inicializamos la aplicación Flask
flask_app = Flask(__name__)

# Punto de entrada principal de la aplicación
def main() -> None:
    setup_db()  # Configuración inicial de la base de datos
    setup_auth(flask_app, Session)  # Configuración del sistema de autenticación
    flask_app.run(debug=True, host="0.0.0.0")  # Ejecutar la aplicación en modo depuración

# Ruta principal que redirige a la página de inicio
@flask_app.route("/")
def index():
    return redirect(url_for("home"))

# Ruta de inicio de sesión
@flask_app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Obtener credenciales desde el formulario
        username = request.form["username"]
        password = request.form["password"]

        if username and password:
            with Session.begin() as session:
                # Verificar las credenciales
                user = (
                    session
                    .query(User)
                    .where(User.username == username and User.password == password)
                    .first()
                )

                if user is None:
                    return {"error": "Credenciales incorrectos"}, 401

                login_user(user)  # Iniciar sesión del usuario

            # Redirigir a la página solicitada o a la página principal
            next = request.args.get("next")
            return redirect(next or url_for("index"))
        else:
            return {"error": "Credenciales incompletos"}
    return render_template("login.html")

# Ruta de registro de nuevos usuarios
@flask_app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        # Obtener los datos del formulario
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Validaciones de contraseña y nombre de usuario
        if password != confirm_password:
            return {"error": "Las contraseñas no coinciden"}, 400

        if len(username) not in range(3, 27):
            return {"error": "El nombre de usuario debe contener como mínimo 3 caracteres y como máximo 26"}, 400

        if len(password) not in range(8, 33):
            return {"error": "La contraseña debe contener como mínimo 8 caracteres y como máximo 32"}, 400

        for c in username:
            # Validar que el nombre de usuario solo contenga caracteres permitidos
            if not (ord(c) in range(48, 58) or ord(c) in range(65, 90) or ord(c) in range(97, 123) or c in [".", "_"]):
                return {"error": "El nombre de usuario no puede contener caracteres especiales"}, 400

        with Session.begin() as session:
            # Verificar si el nombre de usuario ya está en uso
            existing_user = (
                session
                .query(User)
                .where(User.username == username)
                .first()
            )

            if existing_user is not None:
                return {"error": "El nombre de usuario especificado ya está en uso"}, 400

            # Crear un nuevo usuario
            new_user = User(username=username, password=password)
            session.add(new_user)
            session.flush()  # Asegurar que el usuario se persista en la base de datos
            login_user(new_user)  # Iniciar sesión automáticamente

        # Redirigir a la página solicitada o a la página principal
        next = request.args.get("next")
        return redirect(next or url_for("home"))

    return render_template("registro.html")

# Ruta principal (home) accesible solo para usuarios autenticados
@flask_app.route("/home")
@login_required
def home():
    with Session.begin() as session:
        user = session.merge(current_user)  # Actualizar el usuario actual en la sesión
        query = session.query(Post).order_by(Post.created_at.desc())

        # Filtrar publicaciones solo de usuarios seguidos si es necesario
        following_only = request.args.get(
            "following",
            default=False,
            type=lambda x: x.lower() == "true"
        )

        if following_only:
            query = (
                query
                .join(User, User.id == Post.user_id)  # Unir con la tabla de usuarios
                .join(followers_table, followers_table.c.following_id == User.id)  # Unir con la tabla de seguidores
                .where(followers_table.c.follower_id == user.id)  # Filtrar por los usuarios seguidos
            )

        return render_template(
            "index.html",
            current_user=user,  # Pasar el usuario actual al contexto
            posts=query.all(),  # Pasar las publicaciones al contexto
            siguiendo=following_only,  # Indicar si se está filtrando por usuarios seguidos
        )

# Ruta para crear una nueva publicación
@flask_app.route("/post", methods=["POST"])
@login_required
def post():
    with Session.begin() as session:
        user = session.get(User, current_user.id)  # Obtener el usuario actual desde la base de datos

        if user is None:
            return "<h1>Usuario no encontrado</h1>", 404

        try:
            # Crear un nuevo post con el contenido y la imagen opcional
            image = request.files["image"] or None  # Obtener la imagen del formulario
            new_post = Post(
                user_id=user.id,  # Asociar el post al usuario actual
                text=request.form["content"],  # Obtener el texto del post desde el formulario
            )
            if image is not None:
                new_post.image = image.stream.read()  # Leer el contenido de la imagen
        except KeyError:
            return "Json mal formado", 400

        session.add(new_post)  # Agregar el nuevo post a la base de datos

    return redirect(url_for("home"))  # Redirigir a la página principal después de publicar


# Ruta para ver la imagen de un post
@flask_app.route("/post/<int:post_id>/image")
def post_image(post_id: int):
    with Session.begin() as session:
        post = session.get(Post, post_id)  # Obtener el post por ID

        if post is None:
            return "Post not found", 404  # Retornar error si el post no existe

        if post.image is None:
            return "Image not found", 404  # Retornar error si no hay imagen asociada

        # Enviar la imagen como respuesta con el tipo de contenido adecuado
        return send_file(BytesIO(post.image), mimetype="image/gif")

# Ruta para ver el perfil de un usuario
@flask_app.route("/perfil/<username>", methods=["GET"])
@login_required
def perfil(username):
    with Session.begin() as session:
        user = session.query(User).where(User.username == username).one()  # Obtener el usuario por nombre de usuario
        if not user:
            return "<h1>Usuario no encontrado</h1>", 404  # Retornar error si el usuario no existe

        # Cargar las publicaciones del usuario
        user_posts = session.scalars(
            select(Post).where(Post.user_id == user.id).order_by(Post.created_at.desc())
        ).all()

        # Contar la cantidad de seguidores y a cuántas personas sigue
        followers_count = len(user.followers)  # La cantidad de seguidores
        following_count = len(user.following)  # La cantidad de personas a las que sigue

        # Pasar un nuevo objeto user completamente gestionado por la sesión activa
        return render_template(
            "perfil.html",
            user=user,
            posts=user_posts,
            followers_count=followers_count,
            following_count=following_count
        )

# Ruta para seguir a un usuario
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

        return redirect(url_for("perfil", username=user_to_follow.username))

# Ruta para dejar de seguir a un usuario
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

    return redirect(url_for("perfil", username=user_to_unfollow.username))

# Ruta para ver y comentar publicaciones
@flask_app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def publicaciones(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)
        if not post:
            return "<h1>Publicación no encontrada</h1>", 404

        if request.method == 'POST':
            comment_text = request.form['comment']  # Obtener el texto del comentario
            new_comment = Comment(text=comment_text, user_id=current_user.id, post_id=post.id)  # Crear nuevo comentario
            session.add(new_comment)
            return redirect(url_for('publicaciones', post_id=post.id))

        # Cargar comentarios junto con sus respuestas y usuarios asociados
        comments = session.query(Comment).filter_by(post_id=post.id).all()
        for comment in comments:
            session.refresh(comment, ["replies", "user"])  # Asegúrate de cargar las respuestas y usuarios

        return render_template('publicaciones.html', post=post, comments=comments)  # Renderizar la plantilla


# Ruta para eliminar un post
@flask_app.route("/post/<int:post_id>", methods=["DELETE"])
@login_required  # Solo usuarios autenticados pueden eliminar publicaciones
def eliminar_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)  # Obtiene la publicación por su ID

        # Si la publicación no existe, devuelve un error 404
        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        # Si el usuario no es el que creó la publicación, no puede eliminarla
        if current_user.id != post.user.id:
            return "Solo el usuario que publicó el post puede eliminarlo", 403

        # Elimina el post y devuelve un mensaje de éxito
        session.delete(post)
        return "Post eliminado", 200


# Ruta para editar un post
@flask_app.route("/post/<int:post_id>", methods=["PUT"])
@login_required  # Solo usuarios autenticados pueden editar publicaciones
def editar_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)  # Obtiene la publicación por su ID

        # Si la publicación no existe, devuelve un error 404
        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        # Si el usuario no es el que creó la publicación, no puede editarla
        if current_user.id != post.user.id:
            return "Solo el usuario que publicó el post puede eliminarlo", 403

        try:
            body = request.json  # Obtiene el cuerpo del JSON
            if body is None:
                raise KeyError  # Si no hay cuerpo, genera un error
            post.text = body["text"]  # Edita el texto de la publicación
        except KeyError:
            return "Json inválido", 400  # Si hay un error en el JSON, devuelve un mensaje de error

        return "Post editado exitosamente", 200


# Ruta para dar like a un post
@flask_app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required  # Solo usuarios autenticados pueden dar like
def likes_post(post_id):
    with Session.begin() as session:
        post = session.get(Post, post_id)  # Obtiene la publicación por su ID
        user = session.get(User, current_user.id)  # Obtiene el usuario actual

        # Si la publicación no existe, devuelve un error 404
        if post is None:
            return "<h1>Publicación no encontrada</h1>", 404

        # Si el usuario ya le dio like, lo elimina; si no, le da like
        if user in post.likes:
            post.likes.remove(user)
            return {
                "liked": False,
                "likes": len(post.likes),  # Devuelve si el like fue removido y el número de likes
            }, 200
        else:
            post.likes.append(user)
            return {
                "liked": True,
                "likes": len(post.likes),  # Devuelve si el like fue agregado y el número de likes
            }, 200


# Ruta para dar like a un comentario
@flask_app.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required  # Solo usuarios autenticados pueden dar like
def Comentarios_likes(comment_id):
    with Session.begin() as session:
        comment = session.get(Comment, comment_id)  # Obtiene el comentario por su ID
        user = session.get(User, current_user.id)  # Obtiene el usuario actual

        # Si el comentario no existe, devuelve un error 404
        if comment is None:
            return "<h1>Respuesta no encontrada</h1>", 404

        # Si el usuario ya le dio like al comentario, lo elimina; si no, le da like
        if user in comment.likes:
            comment.likes.remove(user)
            return {
                "liked": False,
                "likes": len(comment.likes),  # Devuelve si el like fue removido y el número de likes
            }, 200
        else:
            comment.likes.append(user)
            return {
                "liked": True,
                "likes": len(comment.likes),  # Devuelve si el like fue agregado y el número de likes
            }, 200


# Ruta para responder a un comentario
@flask_app.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required  # Solo usuarios autenticados pueden responder a comentarios
def responder_comentario(comment_id):
    with Session.begin() as session:
        comentario = session.get(Comment, comment_id)  # Obtiene el comentario por su ID
        if not comentario:
            return "<h1>El comentario no existe</h1>", 404  # Si el comentario no existe, devuelve un error

        texto_respuesta = request.form.get('response')  # Obtiene la respuesta del formulario
        if not texto_respuesta or texto_respuesta.strip() == "":  # Si la respuesta está vacía
            return "<h1>El texto de la respuesta no puede estar vacío</h1>", 400

        # Crea una nueva respuesta y la agrega a la base de datos
        nueva_respuesta = Reply(
            comment_id=comment_id,
            user_id=current_user.id,
            text=texto_respuesta.strip()
        )
        session.add(nueva_respuesta)
        return redirect(url_for('publicaciones', post_id=comentario.post_id))  # Redirige a la publicación


# Ruta para dar like a una respuesta
@flask_app.route("/reply/<int:reply_id>/like", methods=["POST"])
@login_required  # Solo usuarios autenticados pueden dar like
def likes_repuestas(reply_id):
    with Session.begin() as session:
        reply = session.get(Reply, reply_id)  # Obtiene la respuesta por su ID
        user = session.get(User, current_user.id)  # Obtiene el usuario actual

        # Si la respuesta no existe, devuelve un error 404
        if reply is None:
            return "<h1>Respuesta no encontrada</h1>", 404

        # Si el usuario ya le dio like a la respuesta, lo elimina; si no, le da like
        if user in reply.likes:
            reply.likes.remove(user)
            return {
                "liked": False,
                "likes": len(reply.likes),  # Devuelve si el like fue removido y el número de likes
            }, 200
        else:
            reply.likes.append(user)
            return {
                "liked": True,
                "likes": len(reply.likes),  # Devuelve si el like fue agregado y el número de likes
            }, 200


# Ruta para cerrar sesión
@flask_app.route("/logout", methods=["POST"])
@login_required  # Solo usuarios autenticados pueden cerrar sesión
def logout():
    flask_login.logout_user()  # Cierra la sesión del usuario actual
    return redirect(url_for("index"))  # Redirige a la página de inicio


# Ruta para obtener el avatar de un usuario
@flask_app.route("/avatar/<int:id>")
def avatar(id: int):
    with Session.begin() as session:
        user = session.get(User, id)  # Obtiene el usuario por su ID

        # Si el usuario no existe, devuelve un error 404
        if user is None:
            return "User not found", 404

        # Si el usuario no tiene avatar, devuelve una imagen por defecto
        if user.avatar is None:
            return send_file("static/images/default_avatar.png", mimetype="image/gif")

        # Si el usuario tiene un avatar, lo devuelve
        return send_file(BytesIO(user.avatar), mimetype="image/gif")


# Ruta para editar las preferencias del usuario (como nombre de usuario, biografía, avatar)
@flask_app.route("/preferencias", methods=["GET", "POST"])
@login_required  # Solo usuarios autenticados pueden editar sus preferencias
def preferencias():
    if request.method == "GET":
        return render_template("preferencias.html")  # Muestra el formulario de preferencias

    with Session.begin() as session:
        user = session.get(User, current_user.id)  # Obtiene el usuario actual
        assert user is not None

        # Actualiza el nombre de usuario y biografía con los datos del formulario
        user.displayname = request.form["displayname"] or None
        user.bio = request.form["bio"] or None

        avatar_file = request.files["avatar"] or None  # Si se sube un nuevo avatar
        if avatar_file is not None:
            user.avatar = avatar_file.stream.read()  # Guarda el nuevo avatar

        return redirect(url_for("perfil", username=user.username))  # Redirige al perfil del usuario


# Arranque de la aplicación Flask
if __name__ == "__main__":
    main()  # Ejecuta la función principal
