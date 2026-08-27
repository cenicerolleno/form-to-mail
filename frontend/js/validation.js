export function validateContactData(data) {
    const errors = {};

    const name = (data.name || '').trim();    
    // Validar nombre
    if (!name) {
        errors.name = 'El nombre es obligatorio.';
    } else if (name.length > 60) {
        errors.name = 'Máximo 60 caracteres';  
    }

    const email = (data.email || '').trim();
    // Validar correo electrónico
    if (!email) {
        errors.email = 'El email es obligatorio.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errors.email = 'El correo electrónico no es válido.';
    }

    const phone = (data.phone || '').trim();
    // Validar teléfono
    if (phone.length > 20) {
        errors.phone = 'Máximo 20 caracteres';
    } else if (phone && !/\d/.test(phone)) {
    errors.phone = 'El teléfono debe contener solo dígitos.';
    }

    const message = (data.message || '').trim();
    // Validar mensaje
    if (!message) {
        errors.message = 'El mensaje es obligatorio.';
    } else if (message.length > 500) {
        errors.message = 'Máximo 500 caracteres.';
    }

    const consent = data.consent;
    // Validar consentimiento
    if (consent !== true) {
        errors.consent = 'El consentimiento es obligatorio.';
    }

    return errors;
}   