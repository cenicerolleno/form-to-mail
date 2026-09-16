from email_validator import validate_email, EmailNotValidError

BREAK_CHARS = ('\n', '\r', '\t')

MAX_NAME = 60
MAX_PHONE = 20
MAX_EMAIL = 254
MAX_MESSAGE = 500


def clean_contact_data(data: dict) -> dict:
    """Devuelve una copia con los valores de texto sin espacios sobrantes.
    Los valores no textuales (consent) se copian tal cual."""
    return {
        key: value.strip() if isinstance(value, str) else value
        for key, value in data.items()
    }


def validate_text_field(value, max_len, required=True, allow_breaks=False) -> str | None:
    if required and not value:
        return 'Este campo es obligatorio.'
    if not value:
        return None
    if not allow_breaks and any(char in value for char in BREAK_CHARS):
        return 'No se permiten saltos de línea.'
    if len(value) > max_len:
        return f'Máximo {max_len} caracteres.'
    return None


def validate_contact_data(data: dict) -> dict:
    """Recibe datos ya limpios (ver clean_contact_data).
    Devuelve un diccionario de errores por campo; vacío = válido."""
    errors = {}

    name_error = validate_text_field(data.get('name'), MAX_NAME)
    if name_error:
        errors['name'] = name_error

    message_error = validate_text_field(data.get('message'), MAX_MESSAGE, allow_breaks=True)
    if message_error:
        errors['message'] = message_error

    email = data.get('email')
    if not email:
        errors['email'] = 'El email es obligatorio.'
    elif len(email) > MAX_EMAIL:
        errors['email'] = f'Máximo {MAX_EMAIL} caracteres.'
    else:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            errors['email'] = 'El formato del correo no es válido.'

    phone = data.get('phone')
    phone_error = validate_text_field(phone, MAX_PHONE, required=False)
    if phone_error:
        errors['phone'] = phone_error
    elif phone and not any(char.isdigit() for char in phone):
        errors['phone'] = 'El teléfono debe contener al menos un dígito numérico.'

    if data.get('consent') is not True:
        errors['consent'] = 'El consentimiento es obligatorio.'

    return errors