from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.problem import Problem

problems_bp = Blueprint('problems', __name__)

@problems_bp.route('/', methods=['GET'])
def get_all_problems():
    problems = Problem.get_all()
    return jsonify(problems), 200

@problems_bp.route('/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    problem = Problem.find_by_id(problem_id)
    if not problem:
        return jsonify({'message': 'Problem not found'}), 404
    
    return jsonify(problem), 200

@problems_bp.route('/', methods=['POST'])
@jwt_required()
def create_problem():
    current_user = get_jwt_identity()
    # Only admin can create problems (simplified)
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    difficulty = data.get('difficulty')
    test_cases = data.get('test_cases')
    
    new_problem = Problem(title, description, difficulty, test_cases)
    new_problem.save()
    
    return jsonify({'message': 'Problem created successfully'}), 201

@problems_bp.route('/<problem_id>/test-cases', methods=['GET'])
def get_problem_test_cases(problem_id):
    problem = Problem.find_by_id(problem_id)
    if not problem:
        return jsonify({'message': 'Problem not found'}), 404
    
    # Return only the test cases
    return jsonify(problem.get('test_cases', [])), 200
