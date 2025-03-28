# from flask import Flask, request, jsonify
# import redis
# from shortener import encode_base62
# from database import URLDatabase
# from flask_cors import CORS

# app = Flask(__name__)
# # CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# # app = Flask(__name__)
# r = redis.Redis(host="redis", port=6379, db=0)
# db = URLDatabase("urls.db")






# BATCH_SIZE = 1000  # Number of IDs to prefetch

# class Counter:
#     def __init__(self):
#         self.current = 0
#         self.max = 0

#     def get_next_id(self):
#         if self.current >= self.max:
#             self.current = r.incrby("global_url_counter", BATCH_SIZE)
#             self.max = self.current + BATCH_SIZE
#         self.current += 1
#         return self.current - 1  # Return the next available ID

# counter = Counter()

# @app.route("/shorten", methods=["POST"])
# def create_short_url():
#     data = request.json
#     original_url = data.get("original_url")
#     if not original_url:
#         return jsonify({"error": "Missing URL"}), 400

#     next_id = counter.get_next_id()  # Use batched counter
#     short_code = encode_base62(next_id).zfill(8)
#     db.insert_url(short_code, original_url)

#     return jsonify({"short_url": f"http://localhost:5002/{short_code}"})



# # @app.route("/shorten", methods=["POST"])
# # def create_short_url():
# #     data = request.json
# #     original_url = data.get("original_url")

# #     if not original_url:
# #         return jsonify({"error": "Missing URL"}), 400

# #     next_id = r.incr("global_url_counter")
# #     short_code = encode_base62(next_id)
# #     db.insert_url(original_url, short_code)

# #     return jsonify({"short_url": f"http://localhost:5002/{short_code}"})

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "healthy"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)







# from flask import Flask, request, jsonify
# import redis
# from shortener import encode_base62
# from database import URLDatabase
# from flask_cors import CORS
# # import validators
# import re
# import threading

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# r = redis.Redis(host="redis", port=6379, db=0)
# db = URLDatabase("urls.db")

# # Batch counter variables (thread-safe)
# BATCH_SIZE = 1000
# lock = threading.Lock()
# batch_start = None
# batch_end = None
# current_counter = None

# def get_next_id():
#     """Fetches the next available ID, using batch counter allocation."""
#     global batch_start, batch_end, current_counter

#     with lock:  # Ensure thread safety
#         if current_counter is None or current_counter >= batch_end:
#             # Request a new batch from Redis
#             batch_start = r.incrby("global_url_counter", BATCH_SIZE)
#             batch_end = batch_start + BATCH_SIZE
#             current_counter = batch_start
        
#         next_id = current_counter
#         current_counter += 1
#         return next_id

# def is_valid_url(url):
#     regex = re.compile(
#         r'^(?:http|ftp)s?://'  # http:// or https://
#         r'\S+$', re.IGNORECASE)
#     return re.match(regex, url) is not None

# # def is_valid_url(url):
# #     url = url.strip()  # Remove leading/trailing whitespace
# #     return validators.url(url)

# @app.route("/shorten", methods=["POST"])
# def create_short_url():
#     data = request.json
#     original_url = data.get("original_url")
#     custom_alias = data.get("custom_alias")
#     expiration_date = data.get("expiration_time")

#     # if not original_url or not is_valid_url(original_url):
#     if not original_url or not is_valid_url(original_url):
#         return jsonify({"error": "Invalid or missing URL"}), 400

#     if custom_alias:
#         if db.get_url_by_short_code(custom_alias):
#             return jsonify({"error": "Custom alias already exists"}), 400
#         short_code = custom_alias
#     else:
#         next_id = get_next_id()  # Fetch an ID from the batch counter
#         short_code = encode_base62(next_id)

#     db.insert_url(short_code, original_url, expiration_time=expiration_date)

#     # domain = "http://short.ly"
#     # return jsonify({"short_url": f"{domain}/{short_code}"})
#     return jsonify({"short_url": f"{short_code}"})

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "healthy"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)


import logging
from flask import Flask, request, jsonify
import redis
from shortener import encode_base62
from database import URLDatabase
from flask_cors import CORS
import re
import threading
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# r = redis.Redis(host="redis", port=6379, db=0)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# db = URLDatabase("urls.db")
# DB_PATH = os.path.join(os.path.dirname(__file__), "urls.db")
DB_PATH = os.getenv("DB_PATH", "/data/urls.db")
db = URLDatabase(DB_PATH)

# Batch counter variables (thread-safe)
BATCH_SIZE = 1000
lock = threading.Lock()
batch_start = None
batch_end = None
current_counter = None

# def get_next_id():
#     """Fetches the next available ID, using batch counter allocation."""
#     global batch_start, batch_end, current_counter

#     with lock:  # Ensure thread safety
#         if current_counter is None or current_counter >= batch_end:
#             # Request a new batch from Redis
#             batch_start = r.incrby("global_url_counter", BATCH_SIZE)
#             batch_end = batch_start + BATCH_SIZE
#             current_counter = batch_start
#             logging.debug("New batch allocated: start=%s, end=%s", batch_start, batch_end)
        
#         next_id = current_counter
#         current_counter += 1
#         logging.debug("Allocated next_id: %s", next_id)
#         return next_id

def get_next_id():
    """Fetches the next available ID, using batch counter allocation adjusted to start from 1."""
    global batch_start, batch_end, current_counter

    with lock:  # Ensure thread safety
        if current_counter is None or current_counter >= batch_end:
            # Request a new batch from Redis.
            # This call returns 1000 on the first batch allocation.
            batch_start = r.incrby("global_url_counter", BATCH_SIZE)
            batch_end = batch_start + BATCH_SIZE
            current_counter = batch_start
            logging.debug("New batch allocated: start=%s, end=%s", batch_start, batch_end)
        
        # Adjust so that the first returned ID is 1.
        next_id = current_counter - (BATCH_SIZE - 1)
        current_counter += 1
        logging.debug("Allocated next_id: %s", next_id)
        return next_id

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'\S+$', re.IGNORECASE)
    result = re.match(regex, url) is not None
    logging.debug("URL validation for '%s': %s", url, result)
    return result

@app.route("/shorten", methods=["POST"])
def create_short_url():
    data = request.json
    original_url = data.get("original_url")
    custom_alias = data.get("custom_alias")
    expiration_date = data.get("expiration_time")
    
    logging.debug("Received shorten request: original_url=%s, custom_alias=%s, expiration_time=%s",
                  original_url, custom_alias, expiration_date)

    if not original_url or not is_valid_url(original_url):
        logging.error("Invalid or missing URL: '%s'", original_url)
        return jsonify({"error": "Invalid or missing URL"}), 400

    if custom_alias:
        if db.get_url_by_short_code(custom_alias):
            logging.error("Custom alias already exists: '%s'", custom_alias)
            return jsonify({"error": "Custom alias already exists"}), 400
        short_code = custom_alias
        logging.debug("Using custom alias as short_code: '%s'", short_code)
    else:
        next_id = get_next_id()  # Fetch an ID from the batch counter
        short_code = encode_base62(next_id)
        logging.debug("Generated short_code from next_id %s: '%s'", next_id, short_code)
    
    db.insert_url(short_code, original_url, expiration_time=expiration_date)
    logging.debug("Inserted URL mapping into DB: '%s' -> '%s'", short_code, original_url)
    
    return jsonify({"short_url": f"{short_code}"})

@app.route("/health", methods=["GET"])
def health():
    logging.debug("Health check requested")
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    logging.debug("Starting write service on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
