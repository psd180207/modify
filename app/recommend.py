import json
import re
from heapq import nlargest
from app.config import SONGS_JSON_PATH
from app.prompt_parser import clamp, normalize_text, normalize_key, split_csv_terms

def load_songs_data():
    try:
        with open(SONGS_JSON_PATH, "r", encoding="utf-8") as file:
            songs = json.load(file)
            return [normalize_song(song) for song in songs]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def normalize_song(song):
    normalized = dict(song)
    normalized["genre"]    = normalize_text(song.get("genre", ""))
    normalized["language"] = normalize_text(song.get("language", ""))
    normalized["language_keys"] = {
        normalize_text(part)
        for part in re.split(r"[/,&]+", normalized["language"])
        if normalize_text(part)
    }
    normalized["primary_emotion"] = normalize_text(song.get("primary_emotion", ""))

    secondary = []
    for item in song.get("secondary_emotions", []):
        secondary.extend(split_csv_terms(item))
    normalized["secondary_emotions"] = secondary

    normalized["artists"]            = [str(a).strip() for a in song.get("artists", [])]
    normalized["artist_keys"]        = [normalize_text(a) for a in normalized["artists"]]
    normalized["artist_search_keys"] = [normalize_key(a)  for a in normalized["artists"]]
    normalized["time_of_day_fit"]    = [normalize_text(v) for v in song.get("time_of_day_fit", [])]
    normalized["activity_tags"]      = [normalize_text(v) for v in song.get("activity_tags", [])]
    normalized["mood_tags"]          = [normalize_text(v) for v in song.get("mood_tags", [])]
    normalized["context_tags"]       = [normalize_text(v) for v in song.get("context_tags", [])]
    normalized["release_era"]        = normalize_text(song.get("release_era", ""))
    normalized["all_tags"] = set(
        normalized["secondary_emotions"]
        + normalized["mood_tags"]
        + normalized["activity_tags"]
        + normalized["context_tags"]
    )
    normalized["energy_level"]      = clamp(float(song.get("energy_level", 0.5)))
    normalized["valence"]           = clamp(float(song.get("valence", 0.5)))
    normalized["speed"]             = clamp(float(song.get("speed", 0.5)))
    normalized["danceability"]      = clamp(float(song.get("danceability", 0.5)))
    normalized["popularity_score"]  = clamp(float(song.get("popularity_score", 0.5)))
    normalized["context_tags_set"]  = set(normalized["context_tags"])
    normalized["activity_tags_set"] = set(normalized["activity_tags"])
    normalized["all_tags_set"]      = set(normalized["all_tags"])
    return normalized

def closeness_score(user_value, song_value):
    if user_value is None:
        return None
    return clamp(1 - abs(user_value - song_value))

def emotion_match_score(user_emotions, song):
    if not user_emotions:
        return None
    score = 0.0
    for emotion in user_emotions:
        if emotion == song["primary_emotion"]:           score = max(score, 1.0)
        elif emotion in song["secondary_emotions"]:      score = max(score, 0.7)
        elif emotion in song["mood_tags"]:               score = max(score, 0.8)
        elif emotion in song["all_tags_set"]:            score = max(score, 0.55)
    return score

def exclusion_penalty(preferences, song):
    penalty = 0.0
    if song["primary_emotion"] in preferences["excluded_emotions"]:          penalty += 0.35
    if preferences["genre"] == "" and song["genre"] in preferences["excluded_genres"]: penalty += 0.25
    if preferences["time"] == "" and any(t in preferences["excluded_times"] for t in song["time_of_day_fit"]): penalty += 0.2
    if preferences["language"] == "" and song["language_keys"] & set(preferences["excluded_languages"]): penalty += 0.25
    if set(song["context_tags"])  & set(preferences["excluded_contexts"]):   penalty += 0.2
    if set(song["activity_tags"]) & set(preferences["excluded_activities"]): penalty += 0.15
    return penalty

def tag_overlap_score(expected_tags, song_tags_set):
    if not expected_tags:
        return None
    overlap = len(set(expected_tags) & song_tags_set)
    return overlap / len(set(expected_tags))

def calculate_score(preferences, song):
    weighted_total = 0.0
    weight_sum     = 0.0
    breakdown      = {}

    def add(name, score, weight):
        nonlocal weighted_total, weight_sum
        if score is None:
            breakdown[name] = None
            return
        weighted_total += weight * score
        weight_sum     += weight
        breakdown[name] = round(score, 2)

    add("emotion",      emotion_match_score(preferences["emotions"], song), 0.18)
    add("energy",       closeness_score(preferences["energy"],      song["energy_level"]), 0.12)
    add("valence",      closeness_score(preferences["valence"],     song["valence"]),      0.10)
    add("speed",        closeness_score(preferences["speed"],       song["speed"]),        0.08)
    add("danceability", closeness_score(preferences["danceability"], song["danceability"]), 0.08)

    time_score = (1.0 if preferences["time"] in song["time_of_day_fit"] else 0.0) if preferences["time"] else None
    add("time", time_score, 0.08)

    genre_score = (1.0 if preferences["genre"] == song["genre"] else 0.0) if preferences["genre"] else None
    add("genre", genre_score, 0.18)

    lang_score = (1.0 if preferences["language"] in song["language_keys"] else 0.0) if preferences["language"] else None
    add("language", lang_score, 0.22)

    ctx_score = tag_overlap_score(preferences["contexts"], song["context_tags_set"])
    if preferences["contexts"] and ctx_score is None: ctx_score = 0.0
    add("context", ctx_score, 0.12)

    act_score = tag_overlap_score(preferences["activities"], song["activity_tags_set"])
    if preferences["activities"] and act_score is None: act_score = 0.0
    add("activity", act_score, 0.10)

    era_score = (1.0 if preferences["era"] == song["release_era"] else 0.0) if preferences["era"] else None
    add("era", era_score, 0.18)

    artist_score = None
    if preferences["artist"]:
        artist_score = 1.0 if normalize_text(preferences["artist"]) in song["artist_keys"] else 0.0
    add("artist", artist_score, 0.34)
    add("popularity", song["popularity_score"], 0.03)

    if preferences["artist"] and artist_score == 1.0:
        weighted_total += 0.08; weight_sum += 0.08
        breakdown["artist_bonus"] = 1.0
    else:
        breakdown["artist_bonus"] = None

    total = (weighted_total / weight_sum) if weight_sum else song["popularity_score"]
    total = clamp(total - exclusion_penalty(preferences, song))
    return total, breakdown

def recommend(songs, preferences, limit=20):
    scored = []
    for song in songs:
        score, breakdown = calculate_score(preferences, song)
        scored.append((score, song, breakdown))
    return nlargest(limit, scored, key=lambda x: x[0])

def get_top_matches(songs, prefs, limit=20):
    scored = []
    top = recommend(songs, prefs, limit=limit)
    for score, song, breakdown in top:
        scored.append({
            "score": round(score * 100),
            "song": song,
            "breakdown": breakdown,
        })
    return scored
