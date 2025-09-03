from flask import Flask
from routes import home, versiones, login
from extensions import mail  
import pdfkit
import platform
import os

app = Flask(__name__)

app.secret_key = "working_agosto"

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'laurapriscilapp@gmail.com'
app.config['MAIL_PASSWORD'] = 'jzgj oldc tznl iwwe'
app.config['MAIL_DEFAULT_SENDER'] = 'laurapriscilapp@gmail.com'

# Detectar sistema operativo y configurar la ruta de wkhtmltopdf
system = platform.system()
if system == "Linux":
    app.config['WKHTMLTOPDF_PATH'] = '/usr/bin/wkhtmltopdf'
elif system == "Windows":
    app.config['WKHTMLTOPDF_PATH'] = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
elif system == "Darwin":  # macOS
    app.config['WKHTMLTOPDF_PATH'] = '/usr/local/bin/wkhtmltopdf'
else:
    app.config['WKHTMLTOPDF_PATH'] = '/usr/bin/wkhtmltopdf'  # Asume Linux por defecto

# Verificar si el ejecutable existe
if not os.path.exists(app.config['WKHTMLTOPDF_PATH']):
    print(f"Advertencia: No se encontró wkhtmltopdf en la ruta: {app.config['WKHTMLTOPDF_PATH']}")
    print("Por favor, instala wkhtmltopdf y actualiza la ruta en la configuración.")

# Inicializar Flask-Mail
mail.init_app(app)

# Configurar pdfkit
try:
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=app.config['WKHTMLTOPDF_PATH'])
    app.pdfkit_config = pdfkit_config
    print("PDFKit configurado correctamente")
except Exception as e:
    print(f"Error al configurar PDFKit: {str(e)}")
    app.pdfkit_config = None

app.register_blueprint(home.bp)
app.register_blueprint(versiones.bp)
app.register_blueprint(login.bp)

if __name__ == '__main__':
    app.run(debug=True)