from flask import Flask, render_template
from routes.customer import customer_bp
from routes.recommend import recommend_bp

# Initialize the Flask app
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(customer_bp)
app.register_blueprint(recommend_bp)

# Define a route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
