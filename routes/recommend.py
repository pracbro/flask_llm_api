from flask import Blueprint, request, render_template
from model.model import get_recommendation

# Create a blueprint for recommendation-related routes
recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend_products():
    customer_data = request.form  # Use form data from HTML

    # Create a prompt for LLM
    prompt = f"Based on the following customer data: {customer_data}, suggest suitable banking lending products."
    
    # Get LLM response
    response = get_recommendation(prompt)
    
    # Render the response in an HTML template
    return render_template('recommendation.html', customer_data=customer_data, recommendation=response)
