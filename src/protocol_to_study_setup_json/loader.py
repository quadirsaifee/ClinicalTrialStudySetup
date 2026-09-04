from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from docx import Document
from pypdf import PdfReader


@dataclass(slots=True)
class ExtractedDocument:
    file_name: str
    file_type: str
    source_path: Path
    extracted_text: str


class ProtocolDocumentLoader:
    """Load and normalize protocol documents from a folder."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

    def load_from_folder(self, folder: str | Path) -> list[ExtractedDocument]:
        root = Path(folder)
        if not root.exists():
            raise FileNotFoundError(f"Input folder does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Expected a folder, got: {root}")

        documents: list[ExtractedDocument] = []
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                documents.append(self.load_document(path))

        if not documents:
            raise ValueError(f"No supported protocol files were found in {root}")

        return documents

    def load_document(self, path: str | Path) -> ExtractedDocument:
        document_path = Path(path)
        file_type = document_path.suffix.lower().lstrip(".")
        extracted_text = self._extract_text(document_path)
        return ExtractedDocument(
            file_name=document_path.name,
            file_type=file_type,
            source_path=document_path,
            extracted_text=extracted_text,
        )

    def combine_text(self, documents: Iterable[ExtractedDocument]) -> str:
        return "\n\n".join(doc.extracted_text.strip() for doc in documents if doc.extracted_text.strip())

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._read_pdf(path)
        if suffix in {".docx", ".doc"}:
            return self._read_docx(path)
        if suffix == ".txt":
            return self._read_text(path)

        return self._read_text(path)

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages).strip()

    def _read_docx(self, path: Path) -> str:
        document = Document(str(path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs)

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")
