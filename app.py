
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app) 

# THE HACK: Pretend to be an Android device so YouTube doesn't block the cloud IP
anti_block_opts = {
    'quiet': True,
    'extractor_args': {'youtube': {'client': ['android']}}, 
}

@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Please provide a song name"}), 400

    ydl_opts = {**anti_block_opts, 'extract_flat': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch7:{query}" 
            info = ydl.extract_info(search_query, download=False)
            
            results = []
            for entry in info.get('entries', []):
                thumb = entry['thumbnails'][0]['url'] if entry.get('thumbnails') else ""
                results.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "artist": entry.get('uploader', 'Unknown Artist'),
                    "thumbnail": thumb
                })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play_song():
    vid_id = request.args.get('id')
    if not vid_id:
        return jsonify({"error": "No Video ID provided"}), 400

    ydl_opts = {**anti_block_opts, 'format': 'bestaudio/best', 'noplaylist': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid_id}", download=False)
            return jsonify({"audio_url": info.get('url')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Cloud servers assign their own port, so we use os.environ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
