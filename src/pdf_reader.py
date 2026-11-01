"""
PDF text extraction using pdfplumber.

Extracts text with layout preserved, so column-based documents
(e.g., multi-year financial statements) retain whitespace between columns.
"""

from pathlib import Path
from dataclasses import dataclass
import pdfplumber


@dataclass
class ExtractedDocument:
    """Container for extracted PDF content."""

    text: str
    source_path: str


def extract_pdf(pdf_path: str | Path) -> ExtractedDocument:
    """
    Extract text from a PDF file with layout preserved.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        ExtractedDocument with text content
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages_text.append(page.extract_text(layout=True))

    text = "\n".join(pages_text)

    return ExtractedDocument(
        text=text,
        source_path=str(pdf_path),
    )


def extract_all_pdfs(pdf_dir: str | Path) -> dict[str, ExtractedDocument]:
    """
    Extract all PDFs from a directory.

    Args:
        pdf_dir: Path to directory containing PDFs

    Returns:
        Dictionary mapping PDF filename to ExtractedDocument
    """
    pdf_dir = Path(pdf_dir)
    results = {}

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        results[pdf_path.name] = extract_pdf(pdf_path)

    return results
