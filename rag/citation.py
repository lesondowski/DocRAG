import re
from pathlib import Path


class CitationMapper:

    def __init__(self, metadatas):
        self.doc_map = self._build_map(metadatas)

    def _build_map(self, metadatas):
        doc_map = {}

        for i, meta in enumerate(metadatas, 1):
            source = Path(meta.get("source", "unknown")).name
            page = meta.get("page", "N/A")
            doc_map[i] = (source, page)

        return doc_map

    def replace(self, text: str) -> str:

        def replace_doc(match):
            doc_id = int(match.group(1))
            source, page = self.doc_map.get(doc_id, ("unknown", "N/A"))
            return f"[{source} - Trang {page}]"

        return re.sub(r"\[DOC (\d+)\]", replace_doc, text)

    def print_citations(self):
        print("\n>> Citations:")
        for i, (source, page) in self.doc_map.items():
            print(f"   [{i}] {source} (Trang {page})")