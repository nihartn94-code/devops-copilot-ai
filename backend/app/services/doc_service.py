import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models import DocSearchResult, DocSearchResponse

class DocumentationService:
    """
    Indexes curated developer documentation files and retrieves relevant
    excerpts with verified source links, providing grounded answers.
    """

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self._load_docs()

    def _get_docs_directory(self) -> Path:
        base = Path(__file__).resolve().parent.parent.parent.parent
        return base / "sample-data" / "docs"

    def _load_docs(self):
        doc_dir = self._get_docs_directory()
        if not doc_dir.exists():
            return

        for f in doc_dir.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                # Extract title from first # header
                title_match = re.search(r"^#\s+(.*)", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f.stem

                # Extract Source URL
                source_match = re.search(r"^Source:\s*(https?://[^\s]+)", content, re.MULTILINE)
                source_url = source_match.group(1).strip() if source_match else None

                # Break into sections
                sections = re.split(r"\n(?=##?\s+)", content)
                for section in sections:
                    sec_title_match = re.search(r"^##?\s+(.*)", section)
                    sec_title = sec_title_match.group(1).strip() if sec_title_match else title
                    self.docs.append({
                        "file_name": f.name,
                        "title": f"{title} › {sec_title}",
                        "source_url": source_url,
                        "content": section.strip()
                    })
            except Exception:
                continue

    def search(self, query: str, max_results: int = 3) -> Tuple[List[DocSearchResult], str]:
        if not self.docs:
            self._load_docs()

        query_tokens = set(re.findall(r"\w+", query.lower()))
        # Remove common stop words
        stop_words = {"how", "what", "to", "in", "a", "the", "for", "is", "of", "and", "or", "on", "with"}
        query_tokens = {t for t in query_tokens if t not in stop_words and len(t) > 2}

        scored_results: List[Tuple[float, Dict[str, Any]]] = []

        for item in self.docs:
            content_lower = item["content"].lower()
            title_lower = item["title"].lower()

            score = 0.0
            for t in query_tokens:
                # Title matches have high weight
                if t in title_lower:
                    score += 3.0
                # Content frequency
                matches = len(re.findall(r"\b" + re.escape(t) + r"\b", content_lower))
                score += min(matches * 0.5, 5.0)

            if score > 0.5:
                scored_results.append((score, item))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        if not scored_results:
            return (
                [],
                "No relevant documentation found in the indexed corpus for this query. "
                "DevOps Copilot AI only cites verified, indexed documents and will not invent unverified sources."
            )

        results: List[DocSearchResult] = []
        for score, item in scored_results[:max_results]:
            # Clean excerpt
            clean_lines = [l for l in item["content"].splitlines() if not l.startswith("#") and not l.startswith("Source:")]
            excerpt = "\n".join(clean_lines[:8]).strip()
            if len(excerpt) > 400:
                excerpt = excerpt[:397] + "..."

            results.append(DocSearchResult(
                title=item["title"],
                source_file=item["file_name"],
                source_url=item["source_url"],
                relevance_score=round(min(score / 10.0, 1.0), 2),
                excerpt=excerpt
            ))

        # Grounded answer synthesis
        top = results[0]
        answer = (
            f"According to the documentation for **{top.title}** ({top.source_file}):\n\n"
            f"{top.excerpt}\n\n"
            f"**Verified Source**: {top.source_url or top.source_file}"
        )

        return results, answer

doc_service = DocumentationService()
