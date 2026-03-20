from pypdf import PdfReader
# Document Processing pipeline in Gemini Cookbook.
""" """
def load_pdf(file_path):
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append({
                "page_number": i + 1,
                "text": text
            })
    return pages
