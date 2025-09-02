from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from conexion import conectar
import hashlib
import binascii
import os
import hmac
from datetime import datetime, timedelta

bp = Blueprint('login', __name__)

@bp.route('/login', methods=['GET'])
def login():
    return render_template("login.html")

@bp.route('/login', methods=['POST'])
def login_post():
    # Obtener los datos del formulario
    username = request.form.get('username')
    password = request.form.get('password')

    # Conectar a la base de datos
    conn = conectar()
    cursor = conn.cursor()

    try:
        # Buscar el usuario en la base de datos
        cursor.execute("""
            SELECT id, username, password_hash, salt, nombre_completo, 
                   bloqueado_hasta, intentos_fallidos 
            FROM usuarios 
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()

        # Verificar si el usuario existe
        if user:
            user_id, username_db, password_hash, salt, nombre_completo, bloqueado_hasta, intentos_fallidos = user
            
            # Verificar si la cuenta está temporalmente bloqueada
            if bloqueado_hasta and bloqueado_hasta > datetime.now():
                return jsonify({'error': 'Cuenta bloqueada temporalmente. Intente más tarde.'}), 400
            
            # Verificar la contraseña
            if verificar_password(password, password_hash, salt):
                # Restablecer intentos fallidos
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = 0, ultimo_acceso = NOW() 
                    WHERE id = %s
                """, (user_id,))
                conn.commit()
                
                # Configurar la sesión
                session['user_id'] = user_id
                session['username'] = username_db
                session['nombre_completo'] = nombre_completo
                session['logged_in'] = True
                
                return jsonify({'message': 'Inicio de sesión exitoso'}), 200
            else:
                # Incrementar intentos fallidos
                intentos_fallidos += 1
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = %s 
                    WHERE id = %s
                """, (intentos_fallidos, user_id))
                conn.commit()
                
                # Verificar si se debe bloquear la cuenta
                if intentos_fallidos >= 5:
                    # Bloquear la cuenta por 30 minutos
                    bloqueado_hasta = datetime.now() + timedelta(minutes=30)
                    cursor.execute("""
                        UPDATE usuarios 
                        SET bloqueado_hasta = %s 
                        WHERE id = %s
                    """, (bloqueado_hasta, user_id))
                    conn.commit()
                    return jsonify({'error': 'Demasiados intentos fallidos. Cuenta bloqueada por 30 minutos.'}), 400
                
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 400
        else:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 400
            
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
        
    finally:
        cursor.close()
        conn.close()

def verificar_password(password, hash_almacenado, sal_almacenada):
    """Verifica si la contraseña coincide con el hash almacenado"""
    try:
        # Convertir la sal hexadecimal a bytes
        sal_bytes = binascii.unhexlify(sal_almacenada)
        
        # Combinar sal y contraseña, luego hashear
        contraseña_con_sal = sal_bytes + password.encode('utf-8')
        hash_obj = hashlib.sha256(contraseña_con_sal)
        hash_calculado = hash_obj.hexdigest()
        
        # Comparar los hashes de forma segura usando hmac.compare_digest
        return hmac.compare_digest(hash_calculado, hash_almacenado)
    except Exception as e:
        print(f"Error al verificar password: {str(e)}")
        return False

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))

# Función para crear un nuevo usuario (útil para el administrador)
@bp.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
        
    username = request.form.get('username')
    password = request.form.get('password')
    nombre_completo = request.form.get('nombre_completo')
    email = request.form.get('email')
    
    # Generar hash y sal para la contraseña
    hash_hex, sal_hex = crear_hash_con_sal(password)
    
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, salt, nombre_completo, email) VALUES (%s, %s, %s, %s, %s)",
            (username, hash_hex, sal_hex, nombre_completo, email)
        )
        conn.commit()
        return jsonify({'message': 'Usuario creado exitosamente'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 400
    finally:
        cursor.close()
        conn.close()

def crear_hash_con_sal(password):
    """Genera un hash seguro con sal para la contraseña"""
    # Generar una sal aleatoria (16 bytes)
    sal = os.urandom(16)
    sal_hex = binascii.hexlify(sal).decode('utf-8')
    
    # Combinar sal y contraseña, luego hashear
    contraseña_con_sal = sal + password.encode('utf-8')
    hash_obj = hashlib.sha256(contraseña_con_sal)
    hash_hex = hash_obj.hexdigest()
    
    return hash_hex, sal_hex

# Ruta para verificar el estado de la sesión
@bp.route('/check_session')
def check_session():
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'nombre_completo': session.get('nombre_completo')
        }), 200
    else:
        return jsonify({'logged_in': False}), 401