from flask import jsonify, Blueprint, request
from services.validation import validate_contact_data
from services.antispam import is_bot, is_rate_limited
from services.mailer import send_email
from config import Config

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact', methods=['POST'])
def contact():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Too many requests"}), 429
    data = request.get_json(silent=True)
    if data is None:
        return (jsonify({"error": "No body in request"}), 400)
    if is_bot(data):
        return (jsonify({"message": "Contact form submitted !"}), 200)
    errors = validate_contact_data(data)
    if errors:
        return (jsonify({"errors": errors}), 400)
    
    result = send_email(data, Config)
    if not result["success"]:
        print(result["error"])
        return (jsonify({"message": "The message could not be sent, please try again in a few minutes.!"}), 502)
    
    

    return (jsonify({"message": "Contact form submitted !"}), 200)
