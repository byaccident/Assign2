import fitz
from ebooklib import epub
import re
import os

def is_header_or_footer(block, page_height):
    """
    Determine if a text block is a header or footer based on its position.
    """
    # bbox is (x0, y0, x1, y1)
    x0, y0, x1, y1 = block['bbox']

    # Heuristic: Headers are in the top 5-8% of the page, Footers in the bottom 5-8%
    header_threshold = page_height * 0.08
    footer_threshold = page_height * 0.92

    if y1 < header_threshold:
        return True
    if y0 > footer_threshold:
        return True

    return False

def extract_text_blocks(doc):
    """
    Extract text blocks from the document, filtering headers and footers.
    Returns a list of (text, font_size, is_bold) tuples or similar structure.
    """
    content_blocks = []

    for page in doc:
        page_height = page.rect.height
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b['type'] == 0: # text block
                if is_header_or_footer(b, page_height):
                    continue

                # Process lines in the block
                block_text = ""
                max_size = 0
                for line in b["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"] + " "
                        if span["size"] > max_size:
                            max_size = span["size"]

                content_blocks.append({
                    "text": block_text.strip(),
                    "size": max_size,
                    "page": page.number
                })

    return content_blocks

def detect_chapters(content_blocks):
    """
    Group content blocks into chapters.
    """
    chapters = []
    current_chapter = {"title": "Start", "content": ""}

    # Heuristic: Calculate average font size to distinguish headings
    sizes = [b["size"] for b in content_blocks if b["text"]]
    if not sizes:
        return [{"title": "Content", "content": ""}]

    avg_size = sum(sizes) / len(sizes)
    # Assuming chapter titles are significantly larger, e.g., 1.2x average or match "Chapter" pattern

    for block in content_blocks:
        text = block["text"]
        size = block["size"]

        is_chapter_start = False

        # Rule 1: Starts with "Chapter" and is reasonably short
        if re.match(r'^Chapter\s+\d+', text, re.IGNORECASE) and len(text) < 50:
            is_chapter_start = True
        # Rule 2: Large font size (simple heuristic)
        elif size > avg_size * 1.3 and len(text) < 80: # Title-like
             is_chapter_start = True

        if is_chapter_start:
            # Save previous chapter if it has content
            if current_chapter["content"].strip():
                chapters.append(current_chapter)
            current_chapter = {"title": text, "content": ""}
        else:
            current_chapter["content"] += f"<p>{text}</p>\n"

    # Append the last chapter
    if current_chapter["content"].strip():
        chapters.append(current_chapter)

    return chapters

def pdf_to_epub(pdf_path: str, output_path: str):
    doc = fitz.open(pdf_path)
    book = epub.EpubBook()

    # Attempt to get metadata from PDF
    meta = doc.metadata
    book.set_identifier('id123456')
    book.set_title(meta.get('title', 'Converted Book') or 'Converted Book')
    book.set_language('en')
    author = meta.get('author', '')
    if author:
        book.add_author(author)

    content_blocks = extract_text_blocks(doc)
    chapter_data = detect_chapters(content_blocks)

    epub_chapters = []

    # If no chapters detected or just one 'Start', treat as one big chapter if it's empty
    if not chapter_data:
         chapter_data = [{"title": "Content", "content": "<p>No text extracted.</p>"}]

    for i, chap in enumerate(chapter_data):
        c_title = chap["title"]
        c_filename = f'chapter_{i}.xhtml'
        c = epub.EpubHtml(title=c_title, file_name=c_filename, lang='en')
        c.content = f"<h1>{c_title}</h1>\n{chap['content']}"
        book.add_item(c)
        epub_chapters.append(c)

    # Define Table of Contents
    book.toc = (epub_chapters)

    # Add Navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define Spine
    book.spine = ['nav'] + epub_chapters

    epub.write_epub(output_path, book, {})
