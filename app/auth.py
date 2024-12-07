from flask import Flask
from flask_login import LoginManager
from sqlalchemy.orm import Session, sessionmaker

from app.entities import User


# Función para configurar la autenticación de usuarios en la aplicación Flask
def setup_auth(app: Flask, DbSession: sessionmaker[Session]) -> None:
    # Crea una instancia de LoginManager que gestionará la autenticación
    login_manager = LoginManager()
    login_manager.init_app(app)  # Inicializa LoginManager con la aplicación Flask
    app.secret_key = "7297c79d0268931ab71a1e9c12ab6daf40c8c18e639fabce8924b5d079aeb108"  # Clave secreta necesaria para sesiones

    # Función que carga al usuario basado en su ID
    def load_user(user_id: str) -> User | None:
        with DbSession.begin() as session:  # Crea una sesión con la base de datos
            session.expire_on_commit = False  # Evita que las instancias se expiren después de una transacción
            return session.query(User).where(User.id == user_id).first()  # Busca al usuario por ID

    # Establece la función que será utilizada por LoginManager para cargar al usuario
    login_manager.user_loader(load_user)
    
    # Define la vista a la que se redirigirá al usuario si no está autenticado
    login_manager.login_view = "login"  # type: ignore

