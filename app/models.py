from pydantic import BaseModel

class YTRequest(BaseModel):
    query: str
    link: str

class ManualRequest(BaseModel):
    emotion: str
    energy: float
    valence: float
    speed: float
    danceability: float
    genre: str
    time: str
    language: str
    era: str
    context: str
    activity: str
    artist: str

class PromptRequest(BaseModel):
    prompt: str

class FaceRequest(BaseModel):
    extra: str

class BrowserFaceRequest(BaseModel):
    emotion: str
    raw_emotion: str
    confidence: float
    region: dict = None
    extra: str = ""
