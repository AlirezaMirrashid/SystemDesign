from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['leetcode_app']
users_collection = db['users']

class User:
    def __init__(self, username, email, password, solved_problems=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.solved_problems = solved_problems or []
        self.id = None
    
    def save(self):
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'solved_problems': self.solved_problems
        }
        
        result = users_collection.insert_one(user_data)
        self.id = str(result.inserted_id)
        return self.id
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def find_by_username(username):
        user_data = users_collection.find_one({'username': username})
        if not user_data:
            return None
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password='',  # Password hash is already stored
            solved_problems=user_data.get('solved_problems', [])
        )
        user.password_hash = user_data['password_hash']
        user.id = str(user_data['_id'])
        return user
    
    @staticmethod
    def find_by_email(email):
        user_data = users_collection.find_one({'email': email})
        if not user_data:
            return None
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password='',  # Password hash is already stored
            solved_problems=user_data.get('solved_problems', [])
        )
        user.password_hash = user_data['password_hash']
        user.id = str(user_data['_id'])
        return user
