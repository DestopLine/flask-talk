import sqlalchemy as sa  # Importa SQLAlchemy bajo el alias 'sa'
from sqlalchemy.orm import declarative_base, sessionmaker  # Importa las funciones necesarias para crear modelos y manejar sesiones

# Crea una conexión a la base de datos SQLite llamada "flask-talk.db"
db = sa.create_engine("sqlite:///flask-talk.db", echo=True)

# Crea un 'Session' para interactuar con la base de datos
Session = sessionmaker(bind=db)

# Crea una clase base para los modelos de la base de datos
# Esta clase es base de todas las clases de modelo
Base = declarative_base()
