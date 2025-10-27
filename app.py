from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import datetime
import tempfile

app = Flask(__name__)
CORS(app)

# ✅ Fetch thumbnail + metadata
@app.route('/thumbnail')
def get_thumbnail():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
            "forcejson": True,
            "no_check_certificate": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Download endpoint
@app.route('/download')
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    date = datetime.datetime.now().strftime("%d%m%Y")
    filename = f"exported_video_{date}.mp4"

    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, filename)

        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4",
            "no_check_certificate": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(output_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return jsonify({"status": "RedClip backend running ✅"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
