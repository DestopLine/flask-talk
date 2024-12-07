# Flask-Talk

Flask-Talk es una aplicación web de red social escrita en el lenguaje de programación Python con el framework web Flask.
Esta app permite crear una cuenta e iniciar sesión, hacer publicaciones con texto e imágenes,
comentar en publicaciones, responder comentarios, darle like a las publicaciones y comentarios
y seguir a otros usuarios.

Las cuentas permiten agregarle una foto de perfil personalizada y una sección "sobre mí", además de un nombre de usuario único y opcionalmente un nombre no único.

La app usa las siguientes tecnologías:
- Python 3
- Flask
- SQLAlchemy
- Flask-Login

## Ejecutar app
Primero se deberá clonar el repositorio:

```sh
git clone https://github.com/DestopLine/flask-talk
```

después se deberá acceder a la carpeta:

```sh
cd flask-talk
```

crear un entorno virtual:

```sh
py -m venv .venv
```

y activar el entorno:
```sh
# Windows
.\.venv\Scripts\activate

# MacOS & Linux
source ./.venv/bin/activate
```

Finalmente solo hace falta instalar las dependencias:
```sh
pip install -r requirements.txt
```

y ejecutar la app:
```sh
# Windows
py main.py

# MacOS & Liux
python3 main.py
```
