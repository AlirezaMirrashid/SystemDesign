
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_TEMP_FOLDER = os.path.join(BASE_DIR, "uploads_temp")
    UPLOAD_FINAL_FOLDER = os.path.join(BASE_DIR, "uploads_final")
    TRANSCODED_FOLDER = os.path.join(BASE_DIR, "transcoded")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "videos.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supported resolutions for adaptive bitrate streaming
    SUPPORTED_BITRATES = {
        "360p": {"resolution": "640x360"},
        "480p": {"resolution": "854x480"},
        "720p": {"resolution": "1280x720"}
    }
    SEGMENT_LENGTH = 5  # seconds per segment for HLS
