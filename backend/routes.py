from flask import jsonify, Blueprint

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def contact():
    return (jsonify({"message": "Contact form submitted !"}), 200)
