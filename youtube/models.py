

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from flask import current_app
import uuid

db = SQLAlchemy()

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, default="UPLOADING")  # UPLOADING, UPLOADED, TRANSCODING, READY
    final_video_path = db.Column(db.String)
    chunks = db.Column(MutableList.as_mutable(db.JSON), default=list)

    def add_chunk(self, chunkid, fingerprint, size, file_path=None, status="NOT_UPLOADED"):
        current_chunks = self.chunks or []
        if any(str(chunk.get("fingerprint")) == str(fingerprint) for chunk in current_chunks):
            return False
        new_chunk = {
            "chunkid": chunkid,
            "fingerprint": fingerprint,
            "size": size,
            "file_path": file_path,
            "status": status
        }
        self.chunks = current_chunks + [new_chunk]
        db.session.commit()
        return True

    def update_chunk_status(self, chunkid, fingerprint, file_path, status="UPLOADED"):
        if not self.chunks:
            current_app.logger.error("No chunks found for video ID: %s", self.id)
            return False
        updated = False
        for i, chunk in enumerate(self.chunks):
            if str(chunk.get("fingerprint")) == str(fingerprint):
                chunk["file_path"] = file_path
                chunk["status"] = status
                chunk["chunkid"] = chunkid
                updated = True
                self.chunks[i] = chunk
                break
        if updated:
            db.session.commit()
        else:
            current_app.logger.warning("No matching fingerprint found for: %s", fingerprint)
        return updated

    def are_all_chunks_uploaded(self):
        if not self.chunks:
            return False
        return all(str(chunk.get("status")) == "UPLOADED" for chunk in self.chunks)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "final_video_path": self.final_video_path,
            "chunks": self.chunks
        }

class VideoFormat(db.Model):
    """
    Stores information about transcoded formats/bitrates for a video.
    Here directory_path will point to the folder containing HLS segments and the manifest file.
    """
    __tablename__ = "video_formats"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String, db.ForeignKey("videos.id"), nullable=False)
    bitrate = db.Column(db.String, nullable=False)  # e.g., "360p", "480p", "720p"
    directory_path = db.Column(db.String, nullable=False)
