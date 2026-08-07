from flask import jsonify, Blueprint, request
from services.validation import validate_contact_data

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True)
    if data is None:
        return (jsonify({"error": "No body in request"}), 400)
    errors = validate_contact_data(data)
    if errors:
        return (jsonify({"errors": errors}), 400)

    return (jsonify({"message": "Contact form submitted !"}), 200)
