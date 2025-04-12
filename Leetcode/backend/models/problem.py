from pymongo import MongoClient
import os
from bson import ObjectId

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['leetcode_app']
problems_collection = db['problems']

class Problem:
    def __init__(self, title, description, difficulty, test_cases):
        self.title = title
        self.description = description
        self.difficulty = difficulty  # 'easy', 'medium', 'hard'
        self.test_cases = test_cases
        self.id = None
    
    def save(self):
        problem_data = {
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'test_cases': self.test_cases
        }
        
        result = problems_collection.insert_one(problem_data)
        self.id = str(result.inserted_id)
        return self.id
    
    @staticmethod
    def find_by_id(problem_id):
        try:
            problem_data = problems_collection.find_one({'_id': ObjectId(problem_id)})
            if not problem_data:
                return None
            
            problem_data['id'] = str(problem_data.pop('_id'))
            return problem_data
        except:
            return None
    
    @staticmethod
    def get_all():
        problems = []
        for problem in problems_collection.find():
            problem['id'] = str(problem.pop('_id'))
            problems.append(problem)
        return problems
