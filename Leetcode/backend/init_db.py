import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add MongoDB initialization script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seed import seed_database

if __name__ == "__main__":
    # Seed the database with sample problems
    seed_database()
    print("Database initialization completed.")
