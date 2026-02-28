"""
PDF Parser for DSE Mathematics curriculum documents and past papers.

Extracts text from PDFs, classifies content type (curriculum, paper, marking scheme),
and chunks intelligently so each chunk retains semantic meaning.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class DSEPDFParser:
    """
    Parses DSE Mathematics PDFs (curriculum guides, past papers, marking schemes)
    and produces structured, chunked text ready for vector embedding.
    """

    # Metadata classification based on filename patterns
    DOCUMENT_TYPES = {
        "curriculum": ["curriculum", "syllabus", "guide"],
        "paper": ["paper_1", "paper_2", "paper1", "paper2"],
        "marking_scheme": ["marking", "scheme", "answer"],
    }

    # DSE Math topic keywords for auto-tagging chunks
    TOPIC_KEYWORDS = {
    "Quadratic equations in one unknown": [
        "Factor method",
        "Form equations from roots",
        "Graphical solution (x-intercepts)",
        "Quadratic formula",
        "Discriminant and nature of roots",
        "Roots and coefficients relations",
        "Complex number arithmetic"
    ],
    "Functions and graphs": [
        "Function concepts",
        "Function representations",
        "Quadratic graph features",
        "Max/min by graph",
        "Algebraic max/min"
    ],
    "Exponential and logarithmic functions": [
        "Rational indices",
        "Laws of indices",
        "Logarithm properties",
        "Exponential/logarithmic graphs",
        "Solve exponential/logarithmic equations",
        "Real-life logarithm applications",
        "Logarithm history"
    ],
    "More about polynomials": [
        "Polynomial long division",
        "Remainder theorem",
        "Factor theorem",
        "GCD and LCM of polynomials",
        "Rational function operations"
    ],
    "More about equations": [
        "Graphical simultaneous solutions",
        "Algebraic simultaneous solutions",
        "Equations transformable to quadratic",
        "Problem solving"
    ],
    "Variations": [
        "Direct variation",
        "Inverse variation",
        "Variation graphs",
        "Joint and partial variation",
        "Real-life variation applications"
    ],
    "Arithmetic and geometric sequences": [
        "Arithmetic sequence properties",
        "Arithmetic general term",
        "Geometric sequence properties",
        "Geometric general term",
        "Sum to n terms",
        "Sum to infinity",
        "Real-life sequence problems"
    ],
    "Inequalities and linear programming": [
        "Compound linear inequalities",
        "Quadratic inequalities graphically",
        "Quadratic inequalities algebraically",
        "Graph linear inequalities",
        "Systems of inequalities",
        "Linear programming"
    ],
    "More about graphs of functions": [
        "Compare function graphs",
        "Solve f(x)=k graphically",
        "Solve inequalities graphically",
        "Function transformations"
    ],
    "Equations of straight lines": [
        "Line equation from conditions",
        "Line features",
        "Line intersections"
    ],
    "Basic properties of circles": [
        "Chord and arc properties",
        "Angle properties",
        "Cyclic quadrilateral properties",
        "Concyclic tests",
        "Tangent properties",
        "Alternate segment theorem",
        "Geometric proofs"
    ],
    "Loci": [
        "Locus concept",
        "Describe and sketch loci",
        "Algebraic locus equations"
    ],
    "Equations of circles": [
        "Circle equation from conditions",
        "Circle features from equation",
        "Line-circle intersections"
    ],
    "More about trigonometry": [
        "Trigonometric functions",
        "Basic trigonometric equations",
        "Advanced trigonometric equations",
        "Triangle area formula",
        "Sine and cosine rules",
        "Heron's formula",
        "Projection concept",
        "Line-plane angle",
        "Three perpendiculars theorem",
        "2D and 3D problems"
    ],
    "Permutations and combinations": [
        "Counting principles",
        "Permutation concept",
        "Combination concept",
        "Simple permutation problems",
        "Simple combination problems"
    ],
    "More about probability": [
        "Set language",
        "Addition law",
        "Multiplication law",
        "Conditional probability",
        "Probability with counting"
    ],
    "Measures of dispersion": [
        "Dispersion concept",
        "Range and IQR",
        "Box-and-whisker diagram",
        "Standard deviation",
        "Compare dispersions",
        "Standard score applications",
        "Effect of operations"
    ],
    "Uses and abuses of statistics": [
        "Sampling techniques",
        "Questionnaire design",
        "Statistical method uses",
        "Evaluate statistical investigations"
    ]
}

    def __init__(self):
        """Initialize the PDF parser."""
        self._pymupdf_available = False
        self._ocr_available = False
        try:
            import pymupdf  # noqa: F401
            self._pymupdf_available = True
        except ImportError:
            try:
                import fitz  # noqa: F401
                self._pymupdf_available = True
            except ImportError:
                print(
                    "⚠️  PyMuPDF not installed. Install with: pip install PyMuPDF\n"
                    "   Without it, only .txt and .md files can be parsed."
                )
        # Check for OCR capability (needed for scanned-image PDFs)
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
            self._ocr_available = True
        except ImportError:
            print(
                "⚠️  pytesseract or Pillow not installed. Scanned PDFs will not be parsed.\n"
                "   Install with: pip install pytesseract Pillow\n"
                "   Also install Tesseract: brew install tesseract"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Parse all supported files in a directory and return chunked documents.

        Args:
            directory_path: Path to the directory containing DSE documents.

        Returns:
            List of chunk dictionaries ready for vector DB ingestion.
        """
        all_chunks: List[Dict[str, Any]] = []
        dir_path = Path(directory_path)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        supported_extensions = {".pdf", ".txt", ".md"}

        for file_path in sorted(dir_path.rglob("*")):
            if file_path.suffix.lower() in supported_extensions:
                print(f"📄 Parsing: {file_path.name}")
                try:
                    chunks = self.parse_file(str(file_path))
                    all_chunks.extend(chunks)
                    print(f"   ✅ Extracted {len(chunks)} chunks")
                except Exception as e:
                    print(f"   ❌ Error parsing {file_path.name}: {e}")

        print(f"\n📊 Total chunks extracted: {len(all_chunks)}")
        return all_chunks

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a single file and return chunked documents with metadata.

        Args:
            file_path: Path to the file.

        Returns:
            List of chunk dictionaries.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract raw text based on file type
        ext = path.suffix.lower()
        if ext == ".pdf":
            raw_text = self._extract_pdf_text(file_path)
        elif ext in (".txt", ".md"):
            raw_text = path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        if not raw_text.strip():
            return []

        # Classify document type from filename
        doc_type = self._classify_document(path.name)

        # Detect year from filename (e.g., 2020_MATH_Paper_1.pdf -> 2020)
        year = self._extract_year(path.name)

        # Detect paper number from filename
        paper_number = self._extract_paper_number(path.name)

        # Chunk the text
        chunks = self._chunk_text(raw_text, doc_type)

        # Build final chunk objects with metadata
        result = []
        for i, chunk_text in enumerate(chunks):
            # Auto-detect topics mentioned in the chunk
            detected_topics = self._detect_topics(chunk_text)

            chunk_doc = {
                "id": f"{path.stem}_chunk_{i:04d}",
                "text": chunk_text,
                "metadata": {
                    "source_file": path.name,
                    "source_path": str(path),
                    "document_type": doc_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks),  # will be updated after loop
                    "year": year,
                    "paper": paper_number,
                    "detected_topics": detected_topics,
                    "subject": "Mathematics",
                },
            }
            result.append(chunk_doc)

        # Update total_chunks now that we know the final count
        for chunk_doc in result:
            chunk_doc["metadata"]["total_chunks"] = len(result)

        return result

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from a PDF using PyMuPDF, with OCR fallback for scanned images."""
        if not self._pymupdf_available:
            raise ImportError(
                "PyMuPDF is required to parse PDFs. "
                "Install with: pip install PyMuPDF"
            )

        try:
            import pymupdf
            doc = pymupdf.open(file_path)
        except ImportError:
            import fitz
            doc = fitz.open(file_path)

        # --- Pass 1: try native text extraction ---
        pages_text = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            # Filter out watermark-only text (e.g. "Scanned by TapScanner")
            cleaned = re.sub(r"(?i)scanned\s+by\s+\S+", "", text).strip()
            if cleaned:
                pages_text.append(f"[Page {page_num + 1}]\n{text}")

        # If we got meaningful text, return it
        if pages_text:
            doc.close()
            return "\n\n".join(pages_text)

        # --- Pass 2: OCR fallback for scanned-image PDFs ---
        if not self._ocr_available:
            doc.close()
            print(f"   ⚠️  No text layer found and OCR not available. Skipping.")
            return ""

        import pytesseract
        from PIL import Image
        import io

        num_pages = doc.page_count
        print(f"   🔍 No text layer detected — running OCR ({num_pages} pages)…")
        ocr_pages = []

        # Build the zoom matrix (works with both pymupdf and fitz namespaces)
        zoom = 300 / 72  # 72 DPI default → 300 DPI
        try:
            import pymupdf as _mu
            mat = _mu.Matrix(zoom, zoom)
        except ImportError:
            import fitz as _mu
            mat = _mu.Matrix(zoom, zoom)

        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Run Tesseract OCR
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                ocr_pages.append(f"[Page {page_num + 1}]\n{text}")

            if (page_num + 1) % 5 == 0:
                print(f"      OCR progress: {page_num + 1}/{num_pages} pages")

        doc.close()
        print(f"   ✅ OCR extracted text from {len(ocr_pages)}/{num_pages} pages")
        return "\n\n".join(ocr_pages)

    # ------------------------------------------------------------------
    # Chunking strategies
    # ------------------------------------------------------------------

    def _chunk_text(
        self,
        text: str,
        doc_type: str,
        max_chunk_size: int = 1000,
        overlap: int = 150,
    ) -> List[str]:
        """
        Split text into semantically meaningful chunks.

        Strategy varies by document type:
        - curriculum: chunk by section headings
        - paper: chunk by question boundaries
        - marking_scheme: chunk by question boundaries (aligned with paper)
        - fallback: sliding window with overlap
        """
        if doc_type == "paper" or doc_type == "marking_scheme":
            chunks = self._chunk_by_questions(text)
            if chunks:
                return chunks

        if doc_type == "curriculum":
            chunks = self._chunk_by_sections(text)
            if chunks:
                return chunks

        # Fallback: sliding window
        return self._chunk_sliding_window(text, max_chunk_size, overlap)

    def _chunk_by_questions(self, text: str) -> List[str]:
        """
        Split exam papers / marking schemes by question numbers.
        Matches patterns like 'Q1.', 'Question 1', '1.', '(1)', etc.
        """
        # Common DSE question delimiters
        pattern = r"(?=(?:^|\n)\s*(?:Q(?:uestion)?\s*\.?\s*)?\d{1,2}\s*[\.\)]\s)"
        parts = re.split(pattern, text)
        parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 30]
        return parts if len(parts) >= 2 else []

    def _chunk_by_sections(self, text: str) -> List[str]:
        """
        Split curriculum / syllabus documents by headings.
        Matches markdown-style (#, ##) or all-caps section titles.
        """
        pattern = r"(?=(?:^|\n)(?:#{1,3}\s|[A-Z][A-Z ]{4,}\n))"
        parts = re.split(pattern, text)
        parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 30]
        return parts if len(parts) >= 2 else []

    def _chunk_sliding_window(
        self, text: str, max_size: int = 1000, overlap: int = 150
    ) -> List[str]:
        """
        Fallback chunker using a sliding window with character overlap.
        Tries to break on paragraph or sentence boundaries.
        """
        chunks: List[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + max_size, text_len)

            # Try to break at paragraph boundary
            if end < text_len:
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + max_size // 2:
                    end = para_break

                # Try sentence boundary if no paragraph break found
                elif end < text_len:
                    sent_break = max(
                        text.rfind(". ", start, end),
                        text.rfind("。", start, end),
                        text.rfind("? ", start, end),
                    )
                    if sent_break > start + max_size // 2:
                        end = sent_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < text_len else text_len

        return chunks

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------

    def _classify_document(self, filename: str) -> str:
        """Classify document type based on filename."""
        name_lower = filename.lower()
        for doc_type, keywords in self.DOCUMENT_TYPES.items():
            if any(kw in name_lower for kw in keywords):
                return doc_type
        return "general"

    def _extract_year(self, filename: str) -> Optional[str]:
        """Extract year from filename (e.g., '2020_MATH_Paper_1.pdf' → '2020')."""
        match = re.search(r"(20\d{2})", filename)
        return match.group(1) if match else None

    def _extract_paper_number(self, filename: str) -> Optional[str]:
        """Extract paper number from filename (e.g., 'Paper_1' → 'Paper 1')."""
        match = re.search(r"[Pp]aper[_\s]?([12])", filename)
        return f"Paper {match.group(1)}" if match else None

    def _detect_topics(self, text: str) -> List[str]:
        """Auto-detect DSE Math topics mentioned in a text chunk."""
        text_lower = text.lower()
        found = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                found.append(topic)
        return found
