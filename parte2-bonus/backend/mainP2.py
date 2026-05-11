from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    #headers que o PDF.js precisa ler para decidir fazer range request
    expose_headers=["Accept-Ranges", "Content-Range", "Content-Length"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

#tamanho de 1MB do chunk
CHUNCK_SIZE = 1024 * 1024

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="arquivo nao suportado")

    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb") as f:
        #carrega todo o documento na ram entao troca por loop que consome o pedaco do chunk
        #f.write(await file.read())

        #processa o documento no tamanho do chunk e salva o bloco na variavel chunk
        while chunk := await file.read(CHUNCK_SIZE): f.write(chunk)

    return {"filename": file.filename, "url": f"http://localhost:8000/pdf/{file.filename}"}


@app.get("/pdf/{filename}")
async def get_document(filename: str, request: Request):
    file_location = UPLOAD_DIR / filename

    if not file_location.exists():
        raise HTTPException(status_code=404, detail="arquivo nao encontrado")

    #pega o tamanho do arquivo por metadado sem precisar ler os bytes
    file_size = file_location.stat().st_size

    #pega o header Range do request HTTP
    range_header = request.headers.get("range")

    #sem Range: devolve o arquivo inteiro avisando que suporta range
    if range_header is None:
        return FileResponse(
            path=file_location,
            media_type="application/pdf",
            headers={"Accept-Ranges": "bytes"}
        )

    #faz o rase dos bytes
    range_str = range_header.replace("bytes=", "")
    range_start, range_end = range_str.split("-")

    start = int(range_start)
    #se o fim nao for especificado, vai ate o final do arquivo
    end = int(range_end) if range_end else file_size - 1
    #garante que o byte final nao ultrapasse o tamanho real do arquivo
    end = min(end, file_size - 1)
    chunk_length = end - start + 1

    #le apenas o tamanho do chunk ao invez de carregar todo o arquivo
    #diferente do wb que escreve o rb le os bytes
    with open(file_location, "rb") as f:
        f.seek(start)
        data = f.read(chunk_length)

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_length),
        "Content-Type": "application/pdf",
    }

    #retorna 206 Partial Content com o pedaco do arquivo
    return Response(content=data, status_code=206, headers=headers)
