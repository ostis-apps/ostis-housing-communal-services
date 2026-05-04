import fitz
from pathlib import Path
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextExtractor:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError('Файл не найден')

    def extract_text(self, encoding='utf8'):
        if self.file_path.suffix == '.txt':
            with open(self.file_path, "r", encoding=encoding) as f:
                text = f.read()
            return {
                "full_text": text,
                "source": str(self.file_path)
            }
        elif self.file_path.suffix == '.pdf':
            doc = fitz.open(self.file_path)
            pages_data = []
            for page_num, page in enumerate(doc):
                blocks = page.get_text("dict")
                page_text = []
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        block_text = " ".join([
                            span["text"]
                            for line in block["lines"]
                            for span in line["spans"]
                            if span["text"].strip()
                        ])
                        if block_text:
                            page_text.append(block_text)
                pages_data.append({
                    "page_num": page_num + 1,
                    "text": "\n".join(page_text)
                })
            doc.close()
            full_text = "\n".join([p["text"] for p in pages_data])
            return {
                "full_text": full_text,
                "pages": pages_data,
                "source": str(self.file_path)
            }
        elif self.file_path.suffix == '.docx':
            doc = Document(self.file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            return {
                "full_text": "\n".join(paragraphs),
                "source": str(self.file_path)
                }
        else:
            raise ValueError(f"Неподдерживаемый формат: {self.file_path.suffix}. Используйте .txt, .pdf или .docx")

    @staticmethod
    def text_to_chunks(text, chunk_size, chunk_overlap):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)

