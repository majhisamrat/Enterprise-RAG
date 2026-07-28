from pathlib import Path

import pymupdf as fitz

def pdf_to_images(file_path: str) -> dict[int, str]:
   
    file_path = Path(file_path)

    output_dir = Path("temp")
    output_dir.mkdir(exist_ok=True)

    images = {}

    with fitz.open(file_path) as pdf:

        for page_index in range(pdf.page_count):

            page = pdf.load_page(page_index)

            pix = page.get_pixmap(dpi=400)

            image_path = output_dir / f"page_{page_index + 1}.png"

            pix.save(image_path)

            images[page_index + 1] = str(image_path)

    return images