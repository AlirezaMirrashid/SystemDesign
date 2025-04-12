# from flask import Flask, redirect, abort, jsonify
# import redis
# from database import URLDatabase

# # app = Flask(__name__)

# from flask_cors import CORS

# app = Flask(__name__)
# # CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# r = redis.Redis(host="redis", port=6379, db=0)
# db = URLDatabase("urls.db")

# @app.route("/<short_code>")
# def redirect_url(short_code):
#     cached_url = r.get(f"url:{short_code}")

#     if cached_url:
#         return redirect(cached_url.decode(), code=302)

#     url_record = db.get_url_by_short_code(short_code)
#     if not url_record:
#         abort(404)

#     r.setex(f"url:{short_code}", 3600, url_record["original_url"])
#     return redirect(url_record["original_url"], code=302)


# @app.route("/lookup/<short_code>", methods=["GET"])
# def lookup_url(short_code):
#     url_record = db.get_url_by_short_code(short_code)
#     if not url_record:
#         return jsonify({"error": "Not Found"}), 404
#     return jsonify({"original_url": url_record["original_url"]})


# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "healthy"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5002, debug=True)



# # read_service.py
# from flask import Flask, redirect, abort, jsonify, request
# import redis
# from database import URLDatabase
# from flask_cors import CORS
# import datetime

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# # Connect to Redis (ensure your Docker networking or host settings allow access)
# r = redis.Redis(host="redis", port=6379, db=0)
# db = URLDatabase("urls.db")

# @app.route("/lookup/<short_code>", methods=["GET"])
# def lookup_url(short_code):
#     # First, try to fetch from Redis cache.
#     cached_url = r.get(f"url:{short_code}")
#     if cached_url:
#         return jsonify({"original_url": cached_url.decode()})
    
#     # Look up in the database.
#     url_record = db.get_url_by_short_code(short_code)
#     if not url_record:
#         return jsonify({"error": "Not Found"}), 404

#     # Optionally check expiration (omitted here for brevity).

#     # Cache the result for 24 hours.
#     r.setex(f"url:{short_code}", 86400, url_record["original_url"])
#     return jsonify({"original_url": url_record["original_url"]})

# @app.route("/<short_code>", methods=["GET"])
# def redirect_url(short_code):
#     # First, try to fetch from Redis cache.
#     cached_url = r.get(f"url:{short_code}")
#     if cached_url:
#         return redirect(cached_url.decode(), code=302)
    
#     # Look up in the database.
#     url_record = db.get_url_by_short_code(short_code)
#     if not url_record:
#         abort(404)
    
#     # Cache the lookup for future requests.
#     r.setex(f"url:{short_code}", 86400, url_record["original_url"])
#     return redirect(url_record["original_url"], code=302)

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "healthy"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5002, debug=True)


import logging
from flask import Flask, redirect, abort, jsonify, request
import redis
import os

from database import URLDatabase
from flask_cors import CORS
import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to Redis (ensure your Docker networking or host settings allow access)
# r = redis.Redis(host="redis", port=6379, db=0)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# DB_PATH = os.path.join(os.path.dirname(__file__), "urls.db")
# db = URLDatabase(DB_PATH)
DB_PATH = os.getenv("DB_PATH", "/data/urls.db")
db = URLDatabase(DB_PATH)

@app.route("/lookup/<short_code>", methods=["GET"])
def lookup_url(short_code):
    logging.debug("Lookup requested for short_code: %s", short_code)
    
    # First, try to fetch from Redis cache.
    cached_url = r.get(f"url:{short_code}")
    if cached_url:
        decoded_url = cached_url.decode()
        logging.debug("Cache hit for %s: %s", short_code, decoded_url)
        return jsonify({"original_url": decoded_url})
    
    logging.debug("Cache miss for %s. Querying database...", short_code)
    # Look up in the database.
    url_record = db.get_url_by_short_code(short_code)
    if not url_record:
        logging.debug("No record found in database for %s", short_code)
        return jsonify({"error": "Not Found"}), 404

    original_url = url_record["original_url"]
    logging.debug("Database hit for %s: %s", short_code, original_url)
    
    # Optionally check expiration (omitted here for brevity).

    # Cache the result for 24 hours.
    r.setex(f"url:{short_code}", 86400, original_url)
    logging.debug("Cached %s -> %s for 24 hours", short_code, original_url)
    return jsonify({"original_url": original_url})

@app.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    logging.debug("Redirect requested for short_code: %s", short_code)
    
    # First, try to fetch from Redis cache.
    cached_url = r.get(f"url:{short_code}")
    if cached_url:
        decoded_url = cached_url.decode()
        logging.debug("Cache hit for %s: %s", short_code, decoded_url)
        return redirect(decoded_url, code=302)
    
    logging.debug("Cache miss for %s. Querying database...", short_code)
    # Look up in the database.
    url_record = db.get_url_by_short_code(short_code)
    if not url_record:
        logging.debug("No record found in database for %s", short_code)
        abort(404)
    
    original_url = url_record["original_url"]
    logging.debug("Database hit for %s: %s", short_code, original_url)
    
    # Cache the lookup for future requests.
    r.setex(f"url:{short_code}", 86400, original_url)
    logging.debug("Cached %s -> %s for 24 hours", short_code, original_url)
    return redirect(original_url, code=302)

@app.route("/health", methods=["GET"])
def health():
    logging.debug("Health check requested")
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    logging.debug("Starting read service on port 5002")
    app.run(host="0.0.0.0", port=5002, debug=True)
