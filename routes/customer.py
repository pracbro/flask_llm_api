from flask import Blueprint, jsonify
from services.customer_service import generate_customer_data

# Create a blueprint for customer-related routes
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/generate-customer', methods=['GET'])
def generate_customer():
    customer_data = generate_customer_data()
    return jsonify(customer_data)
