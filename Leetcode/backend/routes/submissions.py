from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.submission import Submission
from models.problem import Problem
import redis
import json
import uuid

# Initialize Redis connection
redis_client = redis.Redis(host='redis', port=6379, db=0)

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/', methods=['POST'])
@jwt_required()
def submit_solution():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    problem_id = data.get('problem_id')
    code = data.get('code')
    language = data.get('language')
    
    # Validate problem exists
    problem = Problem.find_by_id(problem_id)
    if not problem:
        return jsonify({'message': 'Problem not found'}), 404
    
    # Create a new submission with pending status
    submission = Submission(
        user_id=current_user,
        problem_id=problem_id,
        code=code,
        language=language,
        status='pending'
    )
    submission_id = submission.save()
    
    # Add the job to the queue
    job_id = str(uuid.uuid4())
    job_data = {
        'submission_id': submission_id,
        'problem_id': problem_id,
        'code': code,
        'language': language,
        'user_id': current_user
    }
    
    # Add to Redis queue
    redis_client.lpush('code_execution_queue', json.dumps(job_data))
    
    # Return the submission ID for polling
    return jsonify({
        'submission_id': submission_id,
        'status': 'pending',
        'message': 'Your solution has been queued for execution'
    }), 202

@submissions_bp.route('/status/<submission_id>', methods=['GET'])
@jwt_required()
def get_submission_status(submission_id):
    current_user = get_jwt_identity()
    
    # Get the submission
    submission = Submission.find_by_id(submission_id)
    
    if not submission:
        return jsonify({'message': 'Submission not found'}), 404
    
    # Check if user owns this submission
    if submission['user_id'] != current_user:
        return jsonify({'message': 'Unauthorized access to submission'}), 403
    
    # Return the current status
    return jsonify({
        'submission_id': submission_id,
        'status': submission['status'],
        'execution_time': submission.get('execution_time'),
        'memory_usage': submission.get('memory_usage'),
        'test_results': submission.get('test_results')
    }), 200

@submissions_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_submissions():
    current_user = get_jwt_identity()
    submissions = Submission.find_by_user(current_user)
    
    return jsonify(submissions), 200

@submissions_bp.route('/<submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    submission = Submission.find_by_id(submission_id)
    
    if not submission:
        return jsonify({'message': 'Submission not found'}), 404
    
    return jsonify(submission), 200
