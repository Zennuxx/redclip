# RedClip (Render-ready backend)

This is the backend-only package for **RedClip** (Flask + yt-dlp), ready to deploy on Render.

## Endpoints
- `GET /health` - health check
- `GET /thumbnail?url=<VIDEO_URL>` - returns JSON: { thumbnail: <url>, title: <title> }
- `POST /download` - accepts JSON { "url": "<VIDEO_URL>" } and streams back MP4 attachment named `exported_video_DDMMYYYY.mp4`

## Deploy on Render
1. Create a new GitHub repo and push the contents of this folder.
2. On Render: New -> Web Service -> Connect repo.
3. Environment: Python 3
4. Build Command: `pip install -r requirements.txt`
5. Start Command (Procfile is provided): Render will use it automatically.
6. Deploy. Once live, note your service URL (e.g. https://redclip.onrender.com).

## Notes
- yt-dlp may require `ffmpeg` on the host for some merges. On Render, you can add a build step to install ffmpeg or use a Docker service.
- For production, restrict CORS origins and add authentication/rate-limiting to avoid abuse.
- This project is for personal/educational use. Respect YouTube's Terms of Service.
