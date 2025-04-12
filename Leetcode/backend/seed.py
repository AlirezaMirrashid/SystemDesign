

from pymongo import MongoClient
import os

# Establish a connection to MongoDB
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['leetcode_app']
problems_collection = db['problems']

# Sample problems (with test inputs as valid Python literals)
sample_problems = [
    {
        "title": "Two Sum",
        "description": (
            "Given an array of integers nums and an integer target, return indices of the two numbers "
            "such that they add up to target.\n\n"
            "You may assume that each input would have exactly one solution, and you may not use the same element twice.\n\n"
            "You can return the answer in any order."
        ),
        "difficulty": "easy",
        "test_cases": [
            {"input": "([2,7,11,15], 9)", "expected": "[0,1]"},
            {"input": "([3,2,4], 6)", "expected": "[1,2]"},
            {"input": "([3,3], 6)", "expected": "[0,1]"}
        ],
        "starter_code": {
            "python": (
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        # Write your code here\n"
                "        pass"
            ),
            "javascript": (
                "class Solution {\n"
                "    twoSum(nums, target) {\n"
                "        // Write your code here\n"
                "    }\n"
                "}"
            ),
            "java": (
                "class Solution {\n"
                "    public int[] twoSum(int[] nums, int target) {\n"
                "        // Write your code here\n"
                "        return new int[0];\n"
                "    }\n"
                "}"
            ),
            "cpp": (
                "#include <vector>\n"
                "using namespace std;\n"
                "class Solution {\n"
                "public:\n"
                "    vector<int> twoSum(vector<int>& nums, int target) {\n"
                "        // Write your code here\n"
                "        return {};\n"
                "    }\n"
                "};"
            )
        }
    },
    {
        "title": "Reverse Integer",
        "description": (
            "Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value "
            "to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.\n\n"
            "Assume the environment does not allow you to store 64-bit integers (signed or unsigned)."
        ),
        "difficulty": "medium",
        "test_cases": [
            {"input": "123", "expected": "321"},
            {"input": "-123", "expected": "-321"},
            {"input": "120", "expected": "21"}
        ],
        "starter_code": {
            "python": (
                "class Solution:\n"
                "    def reverse(self, x):\n"
                "        # Write your code here\n"
                "        pass"
            ),
            "javascript": (
                "class Solution {\n"
                "    reverse(x) {\n"
                "        // Write your code here\n"
                "    }\n"
                "}"
            ),
            "java": (
                "class Solution {\n"
                "    public int reverse(int x) {\n"
                "        // Write your code here\n"
                "        return 0;\n"
                "    }\n"
                "}"
            ),
            "cpp": (
                "#include <cstdlib>\n"
                "class Solution {\n"
                "public:\n"
                "    int reverse(int x) {\n"
                "        // Write your code here\n"
                "        return 0;\n"
                "    }\n"
                "};"
            )
        }
    },
    {
        "title": "Longest Palindromic Substring",
        "description": "Given a string s, return the longest palindromic substring in s.",
        "difficulty": "medium",
        "test_cases": [
            {"input": "'babad'", "expected": "'bab'"},
            {"input": "'cbbd'", "expected": "'bb'"},
            {"input": "'a'", "expected": "'a'"}
        ],
        "starter_code": {
            "python": (
                "class Solution:\n"
                "    def longestPalindrome(self, s):\n"
                "        # Write your code here\n"
                "        pass"
            )
            # Extend starter_code for other languages as needed.
        }
    },
    {
        "title": "Median of Two Sorted Arrays",
        "description": (
            "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.\n\n"
            "The overall run time complexity should be O(log (m+n))."
        ),
        "difficulty": "hard",
        "test_cases": [
            {"input": "([1,3], [2])", "expected": "2.0"},
            {"input": "([1,2], [3,4])", "expected": "2.5"},
            {"input": "([0,0], [0,0])", "expected": "0.0"}
        ],
        "starter_code": {
            "python": (
                "class Solution:\n"
                "    def findMedianSortedArrays(self, nums1, nums2):\n"
                "        # Write your code here\n"
                "        pass"
            )
            # Extend for other languages if needed.
        }
    },
    {
        "title": "Valid Parentheses",
        "description": (
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order."
        ),
        "difficulty": "easy",
        "test_cases": [
            {"input": "'()'", "expected": "'true'"},
            {"input": "'()[]{}'", "expected": "'true'"},
            {"input": "'(]'", "expected": "'false'"}
        ],
        "starter_code": {
            "python": (
                "class Solution:\n"
                "    def isValid(self, s):\n"
                "        # Write your code here\n"
                "        pass"
            )
            # Extend for other languages if needed.
        }
    }
]

def seed_database():
    """Seed the database with sample problems."""
    if problems_collection.count_documents({}) > 0:
        print("Problems already exist in the database")
        return
    problems_collection.insert_many(sample_problems)
    print(f"Inserted {len(sample_problems)} sample problems into the database")

if __name__ == "__main__":
    seed_database()
