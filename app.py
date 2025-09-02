from flask import Flask
from routes import home, versiones, login

app = Flask(__name__)

app.secret_key = "working_agosto"

app.register_blueprint(home.bp)
app.register_blueprint(versiones.bp)
app.register_blueprint(login.bp)


if __name__ == '__main__':
    app.run(debug=True)