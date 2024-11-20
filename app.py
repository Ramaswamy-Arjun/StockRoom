from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import os

# Flask app configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Arjun2003%23%40@127.0.0.1/stockroom_db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Replace with a strong secret key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable to save resources

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# User model definition
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Signup route for user registration
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if username or email already exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or Email already exists"}), 400

    # Create a new user instance
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    # Save the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login route for user authentication
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Find the user by username
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password is correct
    if user and user.check_password(password):
        # Create JWT token
        access_token = create_access_token(identity=user.user_id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid username or password"}), 401



@app.route('/myStockroom', methods=['GET'])
@jwt_required(optional=True)  # This decorator ensures the route requires a valid JWT
def my_stockroom():
    try:
        verify_jwt_in_request()  # This will validate the JWT or raise an error
        user_id = get_jwt_identity()
        print(f"Received user_id: {user_id}")  # Debug
        user = User.query.get(user_id)
        if user:
            return render_template('myStockroom.html', username=user.username)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({"error": "Unauthorized access"}), 401

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Main entry point for running the application
if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=5555, debug=True)