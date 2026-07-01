import re
from app.config import (
    LANGUAGE_ALIASES,
    ENERGY_HINTS,
    SPEED_HINTS,
    DANCEABILITY_HINTS,
    VALENCE_BY_EMOTION,
    PHRASE_TO_EMOTION,
    PHRASE_TO_GENRE,
    PHRASE_TO_TIME,
    PHRASE_TO_CONTEXT,
    PHRASE_TO_ACTIVITY,
    ERA_KEYWORDS
)

def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(value, maximum))

def normalize_text(value):
    return str(value).strip().lower()

def normalize_key(value):
    return re.sub(r"[^a-z0-9]+", " ", normalize_text(value)).strip()

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9']+", text.lower())

def split_csv_terms(value):
    return [normalize_text(part) for part in str(value).split(",") if normalize_text(part)]

def build_artist_index(songs):
    artists = set()
    for song in songs:
        for artist in song["artists"]:
            artists.add(artist.strip())
    return sorted(artists, key=str.lower)

def detect_artist(prompt, artist_index):
    prompt_key = normalize_key(prompt)
    matches = [a for a in artist_index if normalize_key(a) in prompt_key]
    return max(matches, key=len) if matches else None

def phrase_positions(text, phrase):
    return [m.start() for m in re.finditer(re.escape(phrase), text)]

def is_negated_phrase(text, phrase):
    filler = r"(?:really|very|so|want|any|more|much|just)"
    pattern = rf"\b(?:not|no|dont|don't|without|except|avoid)\b(?:\s+{filler}){{0,2}}\s+{re.escape(phrase)}\b"
    return re.search(pattern, text) is not None

def collect_detected_values(prompt_text, mapping):
    included, excluded = [], []
    for phrase, value in mapping.items():
        if phrase not in prompt_text:
            continue
        if is_negated_phrase(prompt_text, phrase):
            excluded.append(value)
        else:
            included.append(value)
    return dedupe(included), dedupe(excluded)

def dedupe(values):
    return list(dict.fromkeys(values))

def detect_era(prompt_text):
    for era in ERA_KEYWORDS:
        if era in prompt_text:
            return era.lower()
    return ""

def detect_language(prompt_text):
    detected, excluded = [], []
    for phrase, language in LANGUAGE_ALIASES.items():
        if phrase not in prompt_text:
            continue
        if is_negated_phrase(prompt_text, phrase):
            excluded.append(language)
        else:
            detected.append(language)
    detected  = dedupe(detected)
    excluded  = [l for l in dedupe(excluded) if l not in detected]
    return (detected[0] if detected else ""), excluded

def phrase_average(prompt_text, mapping):
    values = [s for ph, s in mapping.items()
              if ph in prompt_text and not is_negated_phrase(prompt_text, ph)]
    return sum(values) / len(values) if values else None

def detect_known_tags(prompt_text, songs, field_name):
    found = []
    for song in songs:
        for tag in song[field_name]:
            if tag in prompt_text and not is_negated_phrase(prompt_text, tag):
                found.append(tag)
                continue
            split_tag = tag.replace("-", " ")
            if split_tag in prompt_text and not is_negated_phrase(prompt_text, split_tag):
                found.append(tag)
    return dedupe(found)

def parse_prompt(prompt, artist_index, songs):
    prompt_text = normalize_key(prompt)
    artist = detect_artist(prompt, artist_index)
    language, excluded_languages = detect_language(prompt_text)
    emotions, excluded_emotions  = collect_detected_values(prompt_text, PHRASE_TO_EMOTION)
    genres,   excluded_genres    = collect_detected_values(prompt_text, PHRASE_TO_GENRE)
    times,    excluded_times     = collect_detected_values(prompt_text, PHRASE_TO_TIME)
    contexts, excluded_contexts  = collect_detected_values(prompt_text, PHRASE_TO_CONTEXT)
    activities, excluded_activities = collect_detected_values(prompt_text, PHRASE_TO_ACTIVITY)

    contexts   = dedupe(contexts   + detect_known_tags(prompt_text, songs, "context_tags"))
    activities = dedupe(activities + detect_known_tags(prompt_text, songs, "activity_tags"))

    energy      = phrase_average(prompt_text, ENERGY_HINTS)
    speed       = phrase_average(prompt_text, SPEED_HINTS)
    danceability = phrase_average(prompt_text, DANCEABILITY_HINTS)

    if emotions:
        valence = sum(VALENCE_BY_EMOTION.get(e, 0.5) for e in emotions) / len(emotions)
    else:
        valence = None

    if speed is None and energy is not None:
        speed = energy
    if danceability is None and speed is not None and ("dance" in prompt_text or "party" in prompt_text):
        danceability = speed

    return {
        "emotion":            emotions[0] if emotions else None,
        "emotions":           emotions,
        "excluded_emotions":  excluded_emotions,
        "energy":             clamp(energy)      if energy      is not None else None,
        "valence":            clamp(valence)     if valence     is not None else None,
        "speed":              clamp(speed)       if speed       is not None else None,
        "danceability":       clamp(danceability) if danceability is not None else None,
        "time":               times[0] if times else "",
        "excluded_times":     excluded_times,
        "genre":              genres[0] if genres else "",
        "excluded_genres":    excluded_genres,
        "artist":             artist,
        "language":           language,
        "excluded_languages": excluded_languages,
        "contexts":           contexts,
        "excluded_contexts":  excluded_contexts,
        "activities":         activities,
        "excluded_activities":excluded_activities,
        "era":                detect_era(prompt_text),
    }
