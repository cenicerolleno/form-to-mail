from email_validator import validate_email, EmailNotValidError

def validate_contact_data(data):
    errors = {}
    name = data.get('name')
    if not name or not name.strip():
        errors['name'] = 'El nombre es obligatorio.'
    elif len(name.strip()) > 60:
        errors['name'] = 'Máximo 60 caracteres'
        
    email = data.get('email')
    if not email or not email.strip():
        errors['email'] = 'El email es obligatorio.'
    else:
        email_cleaned = email.strip()
        try:
            validate_email(email_cleaned, check_deliverability=False)
        except EmailNotValidError:
            errors['email'] = 'El formato del correo no es válido.'
    
    phone = data.get('phone')
    if phone and phone.strip():
        if len(phone.strip()) > 20:
            errors['phone'] = 'Máximo 20 caracteres'
        
    message = data.get('message')
    if not message or not message.strip():
        errors['message'] = 'El mensaje es obligatorio.'
    elif len(message.strip()) > 500:
        errors['message'] = 'Máximo 500 caracteres'
        
    consent = data.get('consent')
    if consent is not True:
        errors['consent'] = 'El consentimiento es obligatorio.'

    return errors
