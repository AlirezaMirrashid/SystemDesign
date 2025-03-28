

import os
from flask import Blueprint, request, jsonify, send_from_directory, abort, Response, current_app
from models import Video, VideoFormat
from utils.range_utils import parse_range_header

video_bp = Blueprint('video', __name__)

def generate_manifest(video_id):
    """
    Generate a manifest listing available bitrate variants for the video.
    Each entry includes the bitrate and a URL to the HLS manifest.
    """
    variants = VideoFormat.query.filter_by(video_id=video_id).all()
    manifest = []
    for variant in variants:
        # Construct a URL for the HLS manifest served by /stream endpoint
        manifest.append({
            "bitrate": variant.bitrate,
            "playlist_url": f"/stream/{video_id}?bitrate={variant.bitrate}"
        })
    return manifest

@video_bp.route('/videos/<video_id>', methods=['GET'])
def get_video_metadata(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404
    manifest = generate_manifest(video_id)
    return jsonify({
        "video": video.to_dict(),
        "manifest": manifest
    }), 200

@video_bp.route('/videos', methods=['GET'])
def list_videos():
    """
    Return a list of all videos (IDs and titles) so the client can select one.
    """
    videos = Video.query.all()
    return jsonify({
        "videos": [{"id": v.id, "title": v.title} for v in videos]
    }), 200


@video_bp.route('/stream/<video_id>', methods=['GET'])
def stream_video(video_id):
    """
    Returns the master HLS playlist or a specific bitrate playlist.
    """
    bitrate = request.args.get('bitrate')

    if bitrate:
        # Serve a specific bitrate playlist
        vf = VideoFormat.query.filter_by(video_id=video_id, bitrate=bitrate).first()
        if not vf:
            abort(404, f"Bitrate '{bitrate}' not found for this video")
        return send_from_directory(vf.directory_path, "playlist.m3u8", mimetype="application/vnd.apple.mpegurl")
    
    # Serve the master playlist
    variants_folder = os.path.join(current_app.config['TRANSCODED_FOLDER'], video_id)
    master_playlist_path = os.path.join(variants_folder, "master.m3u8")
    if not os.path.exists(master_playlist_path):
        abort(404, "Master playlist not found")

    return send_from_directory(variants_folder, "master.m3u8", mimetype="application/vnd.apple.mpegurl")



@video_bp.route('/stream/<video_id>/<bitrate>/<path:filename>', methods=['GET'])
def stream_segment(video_id, bitrate, filename):
    from models import VideoFormat
    vf = VideoFormat.query.filter_by(video_id=video_id, bitrate=bitrate).first()
    if not vf:
        abort(404, f"Bitrate '{bitrate}' not found for video {video_id}")
    return send_from_directory(vf.directory_path, filename)



@video_bp.route('/stream/<video_id>/master.m3u8', methods=['GET'])
def master_manifest(video_id):
    """
    Serve a master manifest that lists all variant playlists for the video.
    This manifest should reference each bitrate variant.
    """
    variants = VideoFormat.query.filter_by(video_id=video_id).all()
    if not variants:
        abort(404, "No transcoded variants found")
    
    master_lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3"
    ]
    for vf in variants:
        # Assume each variant has a known bandwidth (bitrate in bps) and resolution.
        bandwidth = int(vf.bitrate.replace("p", "")) * 100000  # example conversion
        # You might have additional metadata like resolution; here we simply set a placeholder.
        master_lines.extend([
            f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION=640x360',
            f"/stream/{video_id}?bitrate={vf.bitrate}"
        ])
    master_manifest = "\n".join(master_lines)
    return Response(master_manifest, mimetype="application/vnd.apple.mpegurl")
