import os

EMOTIONS = ["sad", "happy", "calm", "energetic", "romantic", "angry", "love", "devotion"]
GENRES = ["bollywood", "pop", "rock", "lofi", "devotional"]
TIMES = ["morning", "afternoon", "evening", "night"]
ERA_KEYWORDS = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]

LANGUAGE_ALIASES = {
    "hindi": "hindi", "marathi": "marathi", "english": "english",
    "tamil": "tamil", "sanskrit": "sanskrit", "punjabi": "punjabi",
    "telugu": "telugu", "malayalam": "malayalam", "kannada": "kannada",
}

VALENCE_BY_EMOTION = {
    "sad": 0.2, "happy": 0.8, "calm": 0.5, "energetic": 0.9,
    "romantic": 0.7, "angry": 0.3, "love": 0.75, "devotion": 0.55,
}

PHRASE_TO_EMOTION = {
    "sad": "sad", "heartbreak": "sad", "heartbroken": "sad", "breakup": "sad",
    "cry": "sad", "crying": "sad", "melancholy": "sad", "lonely": "sad",
    "happy": "happy", "uplifting": "happy", "cheerful": "happy",
    "feel good": "happy", "fun": "happy", "joy": "happy",
    "calm": "calm", "chill": "calm", "peaceful": "calm", "soothing": "calm",
    "mellow": "calm", "soft": "calm", "relaxing": "calm",
    "energetic": "energetic", "high energy": "energetic", "hype": "energetic",
    "pumped": "energetic", "intense": "energetic", "powerful": "energetic",
    "romantic": "romantic", "romance": "romantic", "date": "romantic",
    "love": "love", "loving": "love",
    "devotion": "devotion", "spiritual": "devotion", "devotional": "devotion",
    "bhakti": "devotion", "prayer": "devotion", "meditation": "devotion",
    "angry": "angry", "furious": "angry", "rage": "angry", "mad": "angry",
}

PHRASE_TO_GENRE = {
    "bollywood": "bollywood", "hindi": "bollywood", "filmy": "bollywood",
    "pop": "pop", "disco": "pop", "retro pop": "pop",
    "rock": "rock", "lofi": "lofi", "lo-fi": "lofi", "lo fi": "lofi",
    "devotional": "devotional", "bhajan": "devotional",
}

PHRASE_TO_TIME = {
    "sunrise": "morning", "morning": "morning", "daytime": "afternoon",
    "afternoon": "afternoon", "sunset": "evening", "evening": "evening",
    "night": "night", "late night": "night", "midnight": "night",
}

PHRASE_TO_CONTEXT = {
    "heartbreak": "heartbreak", "breakup": "heartbreak",
    "late night": "late-night", "midnight": "late-night",
    "date night": "date-night", "date": "date-night",
    "long drive": "long-drive", "night drive": "long-drive",
    "road trip": "road-trip", "roadtrip": "road-trip",
    "solo travel": "solo-travel", "solo trip": "solo-travel",
    "open road": "open-road", "mountains": "mountains",
    "wedding": "wedding", "shaadi": "wedding",
    "family": "family", "friends": "friends",
    "party": "dance-floor", "dance floor": "dance-floor", "club": "dance-floor",
    "celebration": "celebration", "festival": "festival",
    "temple": "temple", "meditation": "meditation",
    "focus": "focus", "study": "focus",
    "thoughtful": "thoughtful", "comeback": "comeback",
    "motivation": "motivation", "workout": "intense-workout", "gym": "intense-workout",
    "city night": "city-night", "retro party": "retro-party",
    "deep listening": "deep-listening", "alone": "alone", "spiritual": "spiritual",
}

PHRASE_TO_ACTIVITY = {
    "study": "study", "focus": "study", "relax": "relax", "sleep": "sleep",
    "travel": "travel", "road trip": "travel", "long drive": "travel",
    "workout": "gym", "gym": "gym", "party": "party", "dance": "party",
}

ENERGY_HINTS = {
    "party": 0.9, "workout": 0.95, "gym": 0.9, "dance": 0.85,
    "energetic": 0.85, "high energy": 0.9, "hype": 0.9, "intense": 0.9,
    "focus": 0.45, "study": 0.35, "relax": 0.2, "calm": 0.25,
    "sleep": 0.1, "slow": 0.2, "soft": 0.25,
}

SPEED_HINTS = {
    "party": 0.9, "workout": 0.9, "gym": 0.9, "dance": 0.85,
    "travel": 0.6, "road trip": 0.6, "study": 0.4, "relax": 0.25,
    "sleep": 0.1, "slow": 0.2, "fast": 0.9, "upbeat": 0.8,
}

DANCEABILITY_HINTS = {
    "party": 0.95, "dance": 0.95, "wedding": 0.9, "club": 0.9,
    "gym": 0.7, "travel": 0.55, "relax": 0.15, "study": 0.1,
    "sleep": 0.05, "upbeat": 0.85,
}

EMOTION_MAP = {
    "happy": "happy", "sad": "sad", "angry": "angry",
    "fear": "angry", "surprise": "energetic",
    "neutral": "calm", "disgust": "angry",
}

FACE_DEFAULTS = {
    "sad":      {"energy": 0.3,  "valence": 0.2,  "speed": 0.35, "danceability": 0.2,  "time": "night"},
    "happy":    {"energy": 0.8,  "valence": 0.85, "speed": 0.75, "danceability": 0.8,  "time": "evening"},
    "calm":     {"energy": 0.35, "valence": 0.55, "speed": 0.35, "danceability": 0.2,  "time": "evening"},
    "energetic":{"energy": 0.9,  "valence": 0.75, "speed": 0.85, "danceability": 0.85, "time": "evening"},
    "angry":    {"energy": 0.85, "valence": 0.3,  "speed": 0.8,  "danceability": 0.6,  "time": "night"},
}

PREFERENCE_KEYS = [
    "emotion", "emotions", "excluded_emotions",
    "energy", "valence", "speed", "danceability",
    "time", "excluded_times", "genre", "excluded_genres",
    "artist", "language", "excluded_languages",
    "contexts", "excluded_contexts", "activities", "excluded_activities", "era",
]

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SONGS_JSON_PATH = os.path.join(DATA_DIR, "songs.json")
