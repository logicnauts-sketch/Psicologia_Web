from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
from extensions import mail
from flask_mail import Message
import pdfkit
import platform
import os

bp = Blueprint("home", __name__)

def create_pdf_with_pdfkit(form_data):
    # Crear HTML para el PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Solicitud de Cita - Psicología y Bienestar</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
            h1 {{ color: #4a4a4a; border-bottom: 2px solid #4a4a4a; padding-bottom: 10px; }}
            .field {{ margin-bottom: 15px; }}
            .label {{ font-weight: bold; color: #333; }}
            .value {{ margin-top: 5px; padding: 8px; background-color: #f9f9f9; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>Solicitud de Cita - Psicología y Bienestar</h1>
        
        <div class="field">
            <div class="label">Nombre:</div>
            <div class="value">{form_data['nombre']}</div>
        </div>
        
        <div class="field">
            <div class="label">Email:</div>
            <div class="value">{form_data['email']}</div>
        </div>
        
        <div class="field">
            <div class="label">Teléfono:</div>
            <div class="value">{form_data['telefono']}</div>
        </div>
        
        <div class="field">
            <div class="label">Motivo de consulta:</div>
            <div class="value">{form_data['motivo']}</div>
        </div>
    """
    
    if form_data.get('mensaje'):
        html_content += f"""
        <div class="field">
            <div class="label">Mensaje adicional:</div>
            <div class="value">{form_data['mensaje']}</div>
        </div>
        """
    
    html_content += f"""
        <div class="field">
            <div class="label">Fecha de solicitud:</div>
            <div class="value">{form_data['fecha_solicitud']}</div>
        </div>
        
        <div style="margin-top: 30px; font-style: italic; color: #777;">
            Este documento fue generado automáticamente desde el sitio web de Psicología y Bienestar.
        </div>
    </body>
    </html>
    """
    
    # Generar PDF
    try:
        pdf = pdfkit.from_string(html_content, False, configuration=current_app.pdfkit_config)
        return pdf
    except Exception as e:
        current_app.logger.error(f"Error al generar PDF: {str(e)}")
        raise

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/solicitar-cita', methods=['POST'])
def solicitar_cita():
    try:
        # Obtener datos del formulario
        form_data = {
            'nombre': request.form.get('nombre'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'motivo': request.form.get('motivo'),
            'mensaje': request.form.get('mensaje', ''),
            'fecha_solicitud': datetime.now().strftime("%d/%m/%Y a las %H:%M")
        }
        
        # Validar datos requeridos
        if not all([form_data['nombre'], form_data['email'], form_data['telefono'], form_data['motivo']]):
            return jsonify({'success': False, 'message': 'Todos los campos obligatorios deben ser completados'})
        
        # Crear PDF
        pdf_data = create_pdf_with_pdfkit(form_data)
        
        # Configurar y enviar correo
        msg = Message(
            subject=f"Nueva Solicitud de Cita - {form_data['nombre']}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[current_app.config.get('CITA_EMAIL_RECIPIENT', 'Laurapriscilapp@gmail.com')],
            body=f"""
            Se ha recibido una nueva solicitud de cita:
            
            Nombre: {form_data['nombre']}
            Email: {form_data['email']}
            Teléfono: {form_data['telefono']}
            Motivo: {form_data['motivo']}
            Mensaje: {form_data['mensaje']}
            
            Fecha de solicitud: {form_data['fecha_solicitud']}
            """
        )
        
        # Adjuntar PDF
        msg.attach("solicitud_cita.pdf", "application/pdf", pdf_data)
        
        # Enviar correo
        mail.send(msg)
        
        # Enviar confirmación al cliente
        client_msg = Message(
            subject="Confirmación de solicitud de cita - Psicología y Bienestar",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[form_data['email']],
            body=f"""
            Hola {form_data['nombre']},
            
            Hemos recibido tu solicitud de cita con la siguiente información:
            
            Motivo: {form_data['motivo']}
            Teléfono de contacto: {form_data['telefono']}
            
            Fecha de solicitud: {form_data['fecha_solicitud']}
            
            Nos pondremos en contacto contigo en un periodo de 24 horas o menos para confirmar tu cita.
            
            Atentamente,
            Lic. Laura Pimentel
            Psicología y Bienestar
            """
        )
        
        mail.send(client_msg)
        
        return jsonify({
            'success': True, 
            'message': '¡Gracias por tu solicitud! En un periodo de 24 horas o menos tendrás una respuesta de nuestros representantes.'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al procesar solicitud de cita: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Error interno del servidor. Por favor, intenta más tarde.'
        })