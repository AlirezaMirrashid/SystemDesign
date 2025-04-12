from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
# from db import mongo_db
# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
mongo_db = client['leetcode_app']
# submissions_collection = db['submissions']

class Submission:
    def __init__(self, user_id=None, problem_id=None, code=None, language=None, 
                 status="pending", execution_time=None, memory_usage=None, 
                 test_results=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.problem_id = problem_id
        self.code = code
        self.language = language
        self.status = status
        self.execution_time = execution_time
        self.memory_usage = memory_usage
        self.test_results = test_results or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.id = None
    
    def save(self):
        submission_data = {
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'code': self.code,
            'language': self.language,
            'status': self.status,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'test_results': self.test_results,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if not self.id:
            result = mongo_db.submissions.insert_one(submission_data)
            self.id = str(result.inserted_id)
        else:
            submission_data['updated_at'] = datetime.utcnow()
            mongo_db.submissions.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': submission_data}
            )
        
        return self.id
    
    @staticmethod
    def find_by_id(submission_id):
        submission = mongo_db.submissions.find_one({'_id': ObjectId(submission_id)})
        if submission:
            submission['id'] = str(submission.pop('_id'))
            return submission
        return None
    
    @staticmethod
    def find_by_user(user_id):
        submissions = list(mongo_db.submissions.find({'user_id': user_id}).sort('created_at', -1))
        for submission in submissions:
            submission['id'] = str(submission.pop('_id'))
        return submissions
    
    @staticmethod
    def update_status(submission_id, status, execution_time=None, memory_usage=None, test_results=None):
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if execution_time is not None:
            update_data['execution_time'] = execution_time
        
        if memory_usage is not None:
            update_data['memory_usage'] = memory_usage
            
        if test_results is not None:
            update_data['test_results'] = test_results
            
        mongo_db.submissions.update_one(
            {'_id': ObjectId(submission_id)},
            {'$set': update_data}
        )
