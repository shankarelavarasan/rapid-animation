from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from ai_processing import process_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(request: Request, file: UploadFile = File(...)):
    tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    video_path = os.path.join(tmp_dir, file.filename)

    contents = await file.read()
    with open(video_path, "wb") as f:
        f.write(contents)

    download_url = process_video(video_path)

    if download_url.startswith("/"):
        base = str(request.base_url).rstrip("/")
        return {"download_url": f"{base}{download_url}"}
    return {"download_url": download_url}