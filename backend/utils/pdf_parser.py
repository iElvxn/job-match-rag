import io
import re
import unicodedata

import PyPDF2


def parse_resume(file) -> str:
    """Extract and clean text from a resume PDF. Accepts FastAPI UploadFile or raw bytes."""
    raw = file if isinstance(file, bytes) else file.file.read()

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(raw))
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}") from e

    pages = [t for page in reader.pages if (t := page.extract_text())]
    cleaned = _clean(" ".join(pages))

    if not cleaned:
        raise ValueError("No text extracted — PDF may be image-based. Upload a text-based PDF.")

    return cleaned


def _clean(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)  # resolve ligatures: ﬁ → fi
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
