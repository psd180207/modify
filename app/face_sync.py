from app.config import EMOTION_MAP, FACE_DEFAULTS, PREFERENCE_KEYS

def build_face_preferences(detected_emotion):
    mapped   = EMOTION_MAP.get(detected_emotion, "calm")
    defaults = FACE_DEFAULTS.get(mapped, FACE_DEFAULTS["calm"])
    return {
        "emotion": mapped, "emotions": [mapped], "excluded_emotions": [],
        "energy": defaults["energy"], "valence": defaults["valence"],
        "speed": defaults["speed"],   "danceability": defaults["danceability"],
        "time": defaults["time"],     "excluded_times": [],
        "genre": "",                  "excluded_genres": [],
        "artist": None,               "language": "",
        "excluded_languages": [],     "contexts": [],
        "excluded_contexts": [],      "activities": [],
        "excluded_activities": [],    "era": "",
    }

def merge_unique(left, right):
    merged = []
    for v in left + right:
        if v not in merged:
            merged.append(v)
    return merged

def blend_numeric_preference(face_value, extra_value):
    if extra_value is None: return face_value
    if face_value  is None: return extra_value
    return (face_value + extra_value) / 2

def merge_preferences(face_preferences, extra_preferences):
    merged = {k: face_preferences[k] for k in PREFERENCE_KEYS}
    extra_emotion_conflicts = (
        bool(extra_preferences["emotion"])
        and extra_preferences["emotion"] != face_preferences["emotion"]
    )

    for key in ["emotions", "excluded_emotions", "excluded_times", "excluded_genres",
                "excluded_languages", "contexts", "excluded_contexts",
                "activities", "excluded_activities"]:
        merged[key] = merge_unique(face_preferences[key], extra_preferences[key])

    for key in ["energy", "valence", "speed", "danceability"]:
        if extra_preferences[key] is not None:
            merged[key] = (
                blend_numeric_preference(face_preferences[key], extra_preferences[key])
                if extra_emotion_conflicts else extra_preferences[key]
            )

    for key in ["time", "genre", "artist", "language", "era"]:
        if extra_preferences[key]:
            merged[key] = extra_preferences[key]

    if face_preferences["emotion"]:
        merged["emotion"] = face_preferences["emotion"]
    elif extra_preferences["emotion"]:
        merged["emotion"] = extra_preferences["emotion"]
    elif merged["emotions"]:
        merged["emotion"] = merged["emotions"][0]

    return merged


