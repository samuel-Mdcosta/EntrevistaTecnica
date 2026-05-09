from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from networkx import is_path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CHUNCK_SIZE = 1024 * 1024

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="arquivo nao suportado")
        

    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "url": f"http://localhost:8000/{file.filename}"}


