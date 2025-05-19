from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from Crypto.Cipher import AES
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Allow CORS from any origin (for local frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
DECRYPTED_DIR = "decrypted"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DECRYPTED_DIR, exist_ok=True)


def pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        key = os.urandom(16)  # Random 128-bit AES key
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted = cipher.encrypt(pad(contents))
        print(cipher)
        file_path = os.path.join(UPLOAD_DIR, f"{image.filename}.enc")
        with open(file_path, "wb") as f:
            f.write(encrypted)

        key_hex = key.hex()  # Return key in hex format to frontend
        return {"message": "Encrypted successfully", "key": key_hex, "filename": f"{image.filename}.enc"}
    except Exception as e:
        return {"error": str(e)}





@app.post("/decrypt")
async def decrypt_image(image: UploadFile = File(...), key: str = Form(...)):
    try:
        contents = await image.read()
        key_bytes = bytes.fromhex(key)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(contents))

        original_filename = image.filename.replace(".enc", "_decrypted")
        output_path = os.path.join(DECRYPTED_DIR, original_filename)

        with open(output_path, "wb") as f:
            f.write(decrypted)

        return FileResponse(output_path, media_type="image/jpeg", filename=original_filename)

    except Exception as e:
        return {"error": str(e)}




#Makes static files accessible at URLs
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")




from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_uploads(request: Request):
    return templates.TemplateResponse("uploads.html", {"request": request})

