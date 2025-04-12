# # import sqlite3
# # import os

# # DB_PATH = os.getenv("DB_PATH", "urls.db")

# # def get_db_connection():
#     # """Creates and returns a database connection."""
#     # conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     # conn.row_factory = sqlite3.Row  # Allows accessing columns by name
#     # return conn

# # def initialize_db():
#     # """Creates the necessary database tables if they do not exist."""
#     # conn = get_db_connection()
#     # cursor = conn.cursor()
#     # cursor.execute("""
#         # CREATE TABLE IF NOT EXISTS urls (
#             # id INTEGER PRIMARY KEY AUTOINCREMENT,
#             # short_code TEXT UNIQUE NOT NULL,
#             # original_url TEXT NOT NULL,
#             # creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             # expiration_time TIMESTAMP NULL,
#             # created_by TEXT NULL
#         # );
#     # """)
#     # conn.commit()
#     # conn.close()

# # def insert_url(short_code, original_url, expiration_time=None, created_by=None):
#     # """Inserts a new short URL into the database."""
#     # conn = get_db_connection()
#     # cursor = conn.cursor()
#     # cursor.execute("""
#         # INSERT INTO urls (short_code, original_url, expiration_time, created_by)
#         # VALUES (?, ?, ?, ?)
#     # """, (short_code, original_url, expiration_time, created_by))
#     # conn.commit()
#     # conn.close()

# # def get_original_url(short_code):
#     # """Retrieves the original URL for a given short code."""
#     # conn = get_db_connection()
#     # cursor = conn.cursor()
#     # cursor.execute("SELECT original_url FROM urls WHERE short_code = ? LIMIT 1", (short_code,))
#     # result = cursor.fetchone()
#     # conn.close()
#     # return result["original_url"] if result else None

# # def delete_expired_urls():
#     # """Removes expired URLs from the database."""
#     # conn = get_db_connection()
#     # cursor = conn.cursor()
#     # cursor.execute("DELETE FROM urls WHERE expiration_time IS NOT NULL AND expiration_time < datetime('now')")
#     # conn.commit()
#     # conn.close()


# # database.py (class-based version)
# import sqlite3
# import os

# DB_PATH = os.getenv("DB_PATH", "urls.db")

# class URLDatabase:
#     def __init__(self, db_path=DB_PATH):
#         self.db_path = db_path
#         self._create_table()
    
#     def _create_table(self):
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS urls (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 short_code TEXT UNIQUE NOT NULL,
#                 original_url TEXT NOT NULL,
#                 creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 expiration_time TIMESTAMP NULL,
#                 created_by TEXT NULL
#             );
#         """)
#         conn.commit()
#         conn.close()
    
#     def insert_url(self, short_code, original_url, expiration_time=None, created_by=None):
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO urls (short_code, original_url, expiration_time, created_by)
#             VALUES (?, ?, ?, ?)
#         """, (short_code, original_url, expiration_time, created_by))
#         conn.commit()
#         conn.close()
    
#     def get_url_by_short_code(self, short_code):
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT original_url, expiration_time FROM urls WHERE short_code = ? LIMIT 1", (short_code,))
#         row = cursor.fetchone()
#         conn.close()
#         if row:
#             return {"original_url": row[0], "expiration_time": row[1]}
#         return None


import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

DB_PATH = os.getenv("DB_PATH", "/data/urls.db")

class URLDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expiration_time TIMESTAMP NULL,
                    created_by TEXT NULL
                );
            """)
            conn.commit()
            logging.debug("Database table 'urls' ensured to exist.")
        except Exception as e:
            logging.error("Error creating table: %s", e)
        finally:
            conn.close()
    
    def insert_url(self, short_code, original_url, expiration_time=None, created_by=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO urls (short_code, original_url, expiration_time, created_by)
                VALUES (?, ?, ?, ?)
            """, (short_code, original_url, expiration_time, created_by))
            conn.commit()
            logging.debug("Inserted URL: %s -> %s", short_code, original_url)
        except Exception as e:
            logging.error("Error inserting URL (%s): %s", short_code, e)
        finally:
            conn.close()
    
    def get_url_by_short_code(self, short_code):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT original_url, expiration_time FROM urls WHERE short_code = ? LIMIT 1", (short_code,))
            row = cursor.fetchone()
            if row:
                logging.debug("Found URL for %s: %s", short_code, row[0])
                return {"original_url": row[0], "expiration_time": row[1]}
            else:
                logging.debug("No URL found for %s", short_code)
                return None
        except Exception as e:
            logging.error("Error retrieving URL for (%s): %s", short_code, e)
            return None
        finally:
            conn.close()
    
    def delete_expired_urls(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM urls WHERE expiration_time IS NOT NULL AND expiration_time < datetime('now')")
            conn.commit()
            logging.debug("Expired URLs deleted.")
        except Exception as e:
            logging.error("Error deleting expired URLs: %s", e)
        finally:
            conn.close()
