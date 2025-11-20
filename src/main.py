from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uvicorn
import shutil
import os
from .converter import pdf_to_epub

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/convert")
def convert_pdf(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = os.path.splitext(file.filename)[0] + ".epub"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    pdf_to_epub(file_location, output_path)

    return FileResponse(output_path, media_type='application/epub+zip', filename=output_filename)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
