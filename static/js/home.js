// Navegación responsive
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Cerrar menú al hacer clic en un enlace
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
    });
});

// Navegación suave al hacer scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Validación del formulario
const formulario = document.getElementById('formulario-cita');
const mensajeExito = document.getElementById('mensaje-exito');

formulario.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    let isValid = true;
    
    // Validar nombre
    const nombre = document.getElementById('nombre');
    const errorNombre = document.getElementById('error-nombre');
    
    if (!nombre.value.trim()) {
        errorNombre.style.display = 'block';
        isValid = false;
    } else {
        errorNombre.style.display = 'none';
    }
    
    // Validar email
    const email = document.getElementById('email');
    const errorEmail = document.getElementById('error-email');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email.value.trim() || !emailRegex.test(email.value)) {
        errorEmail.style.display = 'block';
        isValid = false;
    } else {
        errorEmail.style.display = 'none';
    }
    
    // Validar teléfono
    const telefono = document.getElementById('telefono');
    const errorTelefono = document.getElementById('error-telefono');
    
    if (!telefono.value.trim()) {
        errorTelefono.style.display = 'block';
        isValid = false;
    } else {
        errorTelefono.style.display = 'none';
    }
    
    // Validar motivo
    const motivo = document.getElementById('motivo');
    const errorMotivo = document.getElementById('error-motivo');
    
    if (!motivo.value) {
        errorMotivo.style.display = 'block';
        isValid = false;
    } else {
        errorMotivo.style.display = 'none';
    }
    
    // Si el formulario es válido, enviar al servidor
    if (isValid) {
        // Mostrar estado de carga
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Enviando...';
        submitBtn.disabled = true;
        
        try {
            // Crear FormData con los datos del formulario
            const formData = new FormData(this);
            
            // Enviar datos al servidor
            const response = await fetch('/solicitar-cita', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mostrar mensaje de éxito específico
                mensajeExito.innerHTML = data.message;
                mensajeExito.style.display = 'block';
                formulario.reset();
                
                // Ocultar mensaje después de 8 segundos
                setTimeout(() => {
                    mensajeExito.style.display = 'none';
                }, 8000);
            } else {
                // Mostrar error del servidor
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error al enviar el formulario:', error);
            alert('Error al enviar el formulario. Por favor, intenta de nuevo.');
        } finally {
            // Restaurar estado del botón
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }
});

// Efecto de header al hacer scroll
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.padding = '5px 0';
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.padding = '0';
        header.style.boxShadow = 'none';
    }
});

// Animación de aparición de secciones al hacer scroll
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
});

// Toggle para las cards de servicios
document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
        const detalles = button.previousElementSibling;
        const isOpen = detalles.classList.contains('abierto');
        
        // Cerrar todos los detalles abiertos primero
        document.querySelectorAll('.servicio-detalles.abierto').forEach(openDetalle => {
            if (openDetalle !== detalles) {
                openDetalle.classList.remove('abierto');
                openDetalle.previousElementSibling.classList.remove('abierto');
            }
        });
        
        // Alternar el estado actual
        detalles.classList.toggle('abierto');
        button.classList.toggle('aberto');
        
        // Cambiar el texto del botón
        button.textContent = detalles.classList.contains('abierto') ? 'Menos información' : 'Más información';
    });
});

// Hacer visible la sección de inicio inmediatamente
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('inicio').classList.add('visible');
});