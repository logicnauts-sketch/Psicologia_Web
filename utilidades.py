from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):  # Cambia esto según cómo manejas la sesión
            return redirect(url_for("login.login"))  # Redirige a la ruta de login
        return f(*args, **kwargs)
    return decorated_function

def requires_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect(url_for('login'))  # Redirige al login si no tiene el rol necesario
            return f(*args, **kwargs)
        return decorated_function
    return decorator