import textwrap
import requests

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
TIMEOUT_SECONDS = 10
EMAIL_SUBJECT = "Nuevo mensaje desde el formulario web"

def send_email(data, config):

    text_content = textwrap.dedent(
        f"""
        Nuevo contacto desde el formulario web:
        Nombre: {data.get('name')}
        Email: {data.get('email')}
        Telefono: {data.get('phone') or 'No proporcionado'}
        Mensaje: {data.get('message')}
        """
        )
    payload = {
        "sender": {"email": config.MAIL_FROM},
        "to": [{"email": config.MAIL_TO}],
        "replyTo": {"email": data.get("email")},
        "subject": EMAIL_SUBJECT,
        "textContent": text_content
    }
    headers = {
        "api-key": config.BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(
            BREVO_URL, 
            json=payload, 
            headers=headers, 
            timeout=TIMEOUT_SECONDS
        )

        response.raise_for_status()
        
        return {
            "success": True, 
            "error": None, 
            "status_code": response.status_code
            }
    except requests.exceptions.RequestException as error:
        # None si el fallo fue de conexión: no hubo respuesta de la que sacar el código
        status_code = getattr(error.response, "status_code", None)
        
        return {
            "success": False, 
            "error": str(error), 
            "status_code": status_code
            } 
    

