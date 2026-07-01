import os
import sys

# Ensure the root project directory is in the python path when running this script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import webbrowser
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.config import DATA_DIR
from app.models import YTRequest, ManualRequest, PromptRequest, BrowserFaceRequest
from app.ytmusic_client import get_yt_ids
from app.prompt_parser import parse_prompt, detect_artist
from app.recommend import load_songs_data, get_top_matches
from app.face_sync import (
    build_face_preferences,
    merge_preferences
)
from app.prompt_parser import build_artist_index

app = FastAPI()

SONGS = load_songs_data()
ARTIST_INDEX = build_artist_index(SONGS)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(PROJECT_ROOT, "templates")
static_dir = os.path.join(PROJECT_ROOT, "static")

templates = Jinja2Templates(directory=templates_dir)

# Mount static if it exists
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.post("/api/youtube_id")
def get_yt_id_route(req: YTRequest):
    video_ids = get_yt_ids(req.query, req.link)
    return {"videoIds": video_ids}

@app.post("/recommend/manual")
def recommend_manual(req: ManualRequest):
    preferences = {
        "emotion": req.emotion if req.emotion else "", 
        "emotions": [req.emotion] if req.emotion else [],
        "excluded_emotions": [],
        "energy": req.energy / 10.0 if req.energy > 0 else None,
        "valence": req.valence / 10.0 if req.valence > 0 else None,
        "speed": req.speed / 10.0 if req.speed > 0 else None,
        "danceability": req.danceability / 10.0 if req.danceability > 0 else None,
        "time": req.time if req.time != "(optional)" else "",
        "excluded_times": [],
        "genre": req.genre if req.genre != "(optional)" else "",
        "excluded_genres": [],
        "artist": detect_artist(req.artist, ARTIST_INDEX) if req.artist else None,
        "language": req.language if req.language != "(optional)" else "",
        "excluded_languages": [],
        "contexts": [req.context] if req.context != "(optional)" else [],
        "excluded_contexts": [],
        "activities": [req.activity] if req.activity != "(optional)" else [],
        "excluded_activities": [],
        "era": req.era if req.era != "(optional)" else "",
    }
    return get_top_matches(SONGS, preferences)

@app.post("/recommend/prompt")
def recommend_prompt(req: PromptRequest):
    prefs = parse_prompt(req.prompt, ARTIST_INDEX, SONGS)
    return get_top_matches(SONGS, prefs)

@app.post("/recommend/face-browser")
def recommend_face_browser(req: BrowserFaceRequest):
    face_prefs = build_face_preferences(req.raw_emotion)
    if req.extra.strip():
        extra_prefs = parse_prompt(req.extra.strip(), ARTIST_INDEX, SONGS)
        face_prefs = merge_preferences(face_prefs, extra_prefs)

    return {
        "emotion": req.emotion,
        "raw_emotion": req.raw_emotion,
        "confidence": req.confidence,
        "region": req.region,
        "results": get_top_matches(SONGS, face_prefs),
    }

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    songs_cnt = len(SONGS)
    artist_cnt = len(ARTIST_INDEX)
    genres_cnt = len(set(s.get("genre") for s in SONGS if s.get("genre")))
    
    try:
        html = templates.get_template("index.html").render({"request": request})
        html = html.replace("{songs_cnt}", str(songs_cnt))
        html = html.replace("{artist_cnt}", str(artist_cnt))
        html = html.replace("{genres_cnt}", str(genres_cnt))
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: templates/index.html not found: {e}</h1>", status_code=404)

@app.get("/song-browser", response_class=HTMLResponse)
async def get_song_browser(request: Request):
    try:
        html = templates.get_template("song_browser.html").render({"request": request})
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: templates/song_browser.html not found: {e}</h1>", status_code=404)

@app.get("/songs.json")
async def get_songs_json():
    return SONGS

def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # Only open browser locally (when PORT env var is not set by cloud host)
    if "PORT" not in os.environ:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=port)
