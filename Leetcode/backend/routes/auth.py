from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.find_by_username(username) or User.find_by_email(email):
        return jsonify({'message': 'User already exists'}), 400
    
    new_user = User(username, email, password)
    new_user.save()
    
    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.find_by_username(username)
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.find_by_username(current_user)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'username': user.username,
        'email': user.email,
        'solved_problems': user.solved_problems
    }), 200
