from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os, uuid, shutil

app = FastAPI(title="Whisky Portfolio API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://whisky-ui-connected.vercel.app"],  # Vercel 프론트 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
UPLOAD_DIR = "photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=UPLOAD_DIR), name="photos")

# Model
class WhiskyCreate(BaseModel):
    user_id: str
    name: str
    year: int
    purchase_price: int
    purchase_date: str
    storage_location: str
    image_url: str = ""

class WhiskyOut(BaseModel):
    id: str
    name: str
    year: int
    purchase_price: int
    purchase_date: str
    storage_location: str
    image_url: str = ""

# In-memory DB
whiskies_db = {}

# Routes
@app.post("/whiskies", response_model=WhiskyOut)
def create_whisky(w: WhiskyCreate):
    wid = str(uuid.uuid4())
    whiskies_db[wid] = {**w.dict(), "id": wid}
    return whiskies_db[wid]

@app.get("/whiskies", response_model=List[WhiskyOut])
def list_whiskies():
    return list(whiskies_db.values())

@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": filename}

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return JSONResponse(content={}, status_code=200)