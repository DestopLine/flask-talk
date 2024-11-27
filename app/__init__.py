from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        Nombre = request.form["Nombre"]
        Contraseña = request.form["password"]
        
        if Nombre and Contraseña:
            return redirect(url_for("chat.html",user= Nombre))
        else:
            return None  
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True)
