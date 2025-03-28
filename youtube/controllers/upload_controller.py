
import os, uuid, subprocess
from flask import Blueprint, request, jsonify, current_app
from models import Video, db

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/initiate-upload', methods=['POST'])
def initiate_upload():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    if not title:
        return jsonify({"error": "Title is required"}), 400
    video_id = str(uuid.uuid4())
    video = Video(id=video_id, title=title, description=description)
    db.session.add(video)
    db.session.commit()
    return jsonify({"message": "Upload initiated", "video_id": video.id}), 200

@upload_bp.route('/upload-chunk/<video_id>', methods=['POST'])
def upload_chunk(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({"error": "Invalid video_id"}), 404
    if 'file' not in request.files:
        return jsonify({"error": "No file in request"}), 400
    file = request.files['file']
    chunkid = request.form.get('chunkid')
    fingerprint = request.form.get('fingerprint')
    if not fingerprint:
        return jsonify({"error": "Fingerprint not provided"}), 400
    temp_folder = os.path.join(current_app.config["UPLOAD_TEMP_FOLDER"], video_id)
    os.makedirs(temp_folder, exist_ok=True)
    file_path = os.path.join(temp_folder, f"chunk_{fingerprint}")
    file.save(file_path)
    video.update_chunk_status(chunkid, fingerprint, file_path, status="UPLOADED")
    return jsonify({"message": "Chunk uploaded successfully", "video_id": video_id, "fingerprint": fingerprint}), 200

@upload_bp.route('/register-chunks/<video_id>', methods=['POST'])
def register_chunks(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({"error": "Invalid video_id"}), 404
    data = request.get_json()
    chunks_data = data.get("chunks", [])
    for chunk_info in chunks_data:
        video.add_chunk(chunk_info["chunkid"], chunk_info["fingerprint"], chunk_info["size"])
    db.session.commit()
    return jsonify({"message": "Chunks registered", "video_id": video_id}), 200

@upload_bp.route('/complete-upload/<video_id>', methods=['POST'])
def complete_upload(video_id):
    video = Video.query.get(video_id)
    if not video:
        current_app.logger.error("Invalid video_id: %s", video_id)
        return jsonify({"error": "Invalid video_id"}), 404
    if not video.are_all_chunks_uploaded():
        return jsonify({"error": "Some chunks are missing"}), 406

    final_folder = current_app.config['UPLOAD_FINAL_FOLDER']
    os.makedirs(final_folder, exist_ok=True)
    final_path = os.path.join(final_folder, f"{video_id}.mp4")
    total_written = 0
    try:
        with open(final_path, 'wb') as outfile:
            sorted_chunks = sorted(video.chunks, key=lambda c: int(c["fingerprint"]))
            for chunk in sorted_chunks:
                chunk_path = chunk["file_path"]
                if not os.path.exists(chunk_path):
                    current_app.logger.error("Chunk file does not exist: %s", chunk_path)
                    continue
                with open(chunk_path, 'rb') as infile:
                    data = infile.read()
                    outfile.write(data)
                    total_written += len(data)
        current_app.logger.info("Total bytes written: %d", total_written)
    except Exception as e:
        current_app.logger.exception("Error while combining chunks: %s", e)
        return jsonify({"error": "Error during file combining"}), 500

    video.final_video_path = final_path
    video.status = "UPLOADED"
    db.session.commit()
    return jsonify({"message": "Upload complete", "video_id": video_id, "final_video_path": final_path, "status": video.status}), 200



@upload_bp.route('/transcode/<video_id>', methods=['POST'])
def transcode(video_id):
    """
    Transcode the uploaded video into multiple adaptive bitrate HLS streams and generate a master playlist.
    """
    from models import VideoFormat
    video = Video.query.filter_by(id=video_id).first()
    if not video or video.status != "UPLOADED":
        return jsonify({"error": "Video not found or not in correct state"}), 404

    final_path = video.final_video_path
    variants_folder = os.path.join(current_app.config['TRANSCODED_FOLDER'], video_id)
    os.makedirs(variants_folder, exist_ok=True)
    
    master_playlist_path = os.path.join(variants_folder, "master.m3u8")
    
    hls_manifest_files = []
    supported = current_app.config['SUPPORTED_BITRATES']
    segment_length = current_app.config['SEGMENT_LENGTH']

    master_playlist_content = "#EXTM3U\n"

    for bitrate, opts in supported.items():
        resolution = opts["resolution"]
        output_dir = os.path.join(variants_folder, bitrate)
        os.makedirs(output_dir, exist_ok=True)
        
        output_manifest = os.path.join(output_dir, "playlist.m3u8")
        cmd = [
            "ffmpeg",
            "-i", final_path,
            "-vf", f"scale={resolution}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-hls_time", str(segment_length),
            "-hls_playlist_type", "vod",
            "-hls_base_url", f"/stream/{video_id}/{bitrate}/",  
            "-hls_segment_filename", os.path.join(output_dir, "segment%d.ts"),
            output_manifest
        ]
        current_app.logger.info("Transcoding %s to %s (%s)...", video_id, bitrate, resolution)
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Add the bitrate variant to the master playlist
        master_playlist_content += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={resolution}\n"
        master_playlist_content += f"/stream/{video_id}/{bitrate}/playlist.m3u8\n"

        # Save variant information to the database
        vf = VideoFormat(video_id=video_id, bitrate=bitrate, directory_path=output_dir)
        db.session.add(vf)
        hls_manifest_files.append({"bitrate": bitrate, "playlist": output_manifest})

    # Save the master playlist
    with open(master_playlist_path, "w") as master_file:
        master_file.write(master_playlist_content)

    db.session.commit()
    video.status = "READY"
    db.session.commit()

    return jsonify({
        "message": "Transcoding complete.",
        "video_id": video_id,
        "status": video.status,
        "variants": hls_manifest_files,
        "master_playlist": f"/stream/{video_id}/master.m3u8"
    }), 200
