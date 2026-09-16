# Copyright (c) 2026 Mauro Nolan Fernández. Todos los derechos reservados.
import json
import logging
from flask import jsonify, Blueprint, request
from services.validation import clean_contact_data, validate_contact_data
from services.antispam import is_bot, is_rate_limited, get_client_ip
from services.mailer import send_email
from config import Config

logger = logging.getLogger(__name__)
contact_bp = Blueprint('contact', __name__)

# Códigos de Brevo que indican que el dato del usuario no es válido
# (típicamente un replyTo que Brevo rechaza). Reintentar no sirve: es un 400.
USER_ERROR_STATUS = (400,)

# Campos que se vuelcan al log cuando una solicitud no llega a entregarse.
# El honeypot no se registra: no aporta nada y solo lo rellenan los bots,
# que nunca llegan hasta aquí.
LOGGABLE_FIELDS = ("name", "email", "phone", "message")

SUCCESS_MESSAGE = "Solicitud enviada correctamente."


def _loggable(data):
    return {field: data.get(field) for field in LOGGABLE_FIELDS}


@contact_bp.route('/contact', methods=['POST'])
def contact():
    ip = get_client_ip(request.headers, request.remote_addr, Config.TRUST_PROXY)
    if is_rate_limited(ip):
        logger.warning("Rate limit activado. IP: %s", ip)
        return jsonify({"error": "Demasiadas peticiones."}), 429

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Petición sin cuerpo."}), 400

    data = clean_contact_data(data)

    if is_bot(data):
        return jsonify({"message": SUCCESS_MESSAGE}), 200

    errors = validate_contact_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    result = send_email(data, Config)
    if not result["success"]:
        logger.error(
            "Fallo al enviar email. status=%s error=%s",
            result["status_code"],
            result["error"],
        )
        # Rescate mínimo: la solicitud queda en el log para poder contestarla
        # a mano. No es una dead letter queue — no hay reintento ni bandeja:
        # es una línea buscable en el panel de la plataforma.
        logger.error(
            "SOLICITUD NO ENTREGADA: %s",
            json.dumps(_loggable(data), ensure_ascii=False),
        )
        if result["status_code"] in USER_ERROR_STATUS:
            return jsonify({
                "errors": {"email": "El proveedor de correo ha rechazado esta dirección."}
            }), 400
        return jsonify({
            "error": "No se ha podido enviar el mensaje. Inténtalo de nuevo en unos minutos."
        }), 502

    return jsonify({"message": SUCCESS_MESSAGE}), 200