from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password:
            return redirect(url_for("index"))
        else:
            return "<h1>Intento de inicio de sesion fallido, intentar de nuevo</h1>"
    return render_template("login.html")

@app.route("/post", methods=["POST"])
def create_post():
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
