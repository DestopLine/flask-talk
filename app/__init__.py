from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        Nombre = request.form["Nombre"]
        Contraseña = request.form["password"]
        
        if Nombre and Contraseña:
            return redirect(url_for("chat",user= Nombre))
        else:
            return "INGRESAR DATOS VALIDOS"
    return render_template("index.html")

@app.route("/chat")
def chat():
    user = request.args.get("Usuario","Usuario desconocido")
    return render_template("chat.html",user=user)

if __name__ == "__main__":
    app.run(debug=True)
