from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import tempfile, os, datetime, shutil
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # In production, restrict origins

def format_date_ddmmyyyy(dt=None):
    dt = dt or datetime.datetime.now()
    return dt.strftime('%d%m%Y')

@app.route('/health')
def health():
    return jsonify({'status':'ok'})

@app.route('/thumbnail')
def thumbnail():
    url = request.args.get('url') or ''
    if not url:
        return jsonify({'error':'No url provided'}), 400
    # Use yt-dlp to extract info (no download) and return thumbnail URL if available
    ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            thumb = info.get('thumbnail') or info.get('thumbnails') and info.get('thumbnails')[-1].get('url')
            title = info.get('title') if 'title' in info else ''
            return jsonify({'thumbnail': thumb, 'title': title})
    except Exception as e:
        return jsonify({'error':'Failed to extract thumbnail', 'details': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json() or {}
    url = data.get('url') or ''
    if not url:
        return jsonify({'error':'No URL provided'}), 400

    tmpdir = tempfile.mkdtemp(prefix='redclip_')
    outtmpl = os.path.join(tmpdir, 'exported.%(ext)s')
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        # find the downloaded file in tmpdir
        files = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir,f))]
        if not files:
            shutil.rmtree(tmpdir, ignore_errors=True)
            return jsonify({'error':'No file downloaded'}), 500
        filepath = os.path.join(tmpdir, files[0])
        fname = f"exported_video_{format_date_ddmmyyyy()}.mp4"
        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass
            return response
        return send_file(filepath, mimetype='video/mp4', as_attachment=True, download_name=fname)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({'error':'Download failed', 'details': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
