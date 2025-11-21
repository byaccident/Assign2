from fastapi.testclient import TestClient
from src.main import app
import os
import fitz

client = TestClient(app)

def create_dummy_pdf(filename):
    doc = fitz.open()
    page = doc.new_page()

    # Add Header
    page.insert_text((50, 30), "This is a header", fontsize=10)

    # Add Chapter Title
    page.insert_text((50, 100), "Chapter 1: The Beginning", fontsize=20)

    # Add Body Text
    page.insert_text((50, 150), "This is the body text of the first chapter.", fontsize=12)
    page.insert_text((50, 170), "More text goes here.", fontsize=12)

    # Add Footer
    page.insert_text((50, 800), "Page 1", fontsize=10)

    doc.save(filename)
    doc.close()

def test_convert_endpoint():
    pdf_filename = "test.pdf"
    create_dummy_pdf(pdf_filename)

    try:
        with open(pdf_filename, "rb") as f:
            response = client.post("/convert", files={"file": ("test.pdf", f, "application/pdf")})

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/epub+zip"

        # Save the output to inspect if needed, or just verify it's not empty
        assert len(response.content) > 0

        # We could potentially inspect the epub content here using ebooklib to verify chapters
        # but verifying the HTTP response is a good first step.

    finally:
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
