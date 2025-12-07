from __future__ import annotations
from typing import List, Dict, Set, Tuple, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from .url_utils import normalise_url, same_subdomain, canonicalize_start

class SequentialCrawler:
    """
    Minimal sequential crawler:
    - No network in tests: expects a 'fetcher' with .fetch(url) -> (status, text, content_type)
    - Enforces same-subdomain scope
    - Returns visit results rather than printing
    """
    def __init__(self, start_url: str, fetcher, max_pages: int = 500, max_depth: int = 32):
        self.start = canonicalize_start(start_url)
        self.root_netloc = urlparse(self.start).netloc
        self.fetcher = fetcher
        self.max_pages = max_pages
        self.max_depth = max_depth

    def run(self) -> List[Dict]:
        queue: List[Tuple[str, int]] = [(self.start, 0)]
        seen: Set[str] = set()
        results: List[Dict] = []

        while queue and len(seen) < self.max_pages:
            url, depth = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            status, text, ctype = self.fetcher.fetch(url)
            if status != 200 or not ctype or "text/html" not in ctype.lower():
                results.append({"url": url, "links": []})
                continue

            links = self._extract_inbounds(url, text)
            links = sorted(links)
            results.append({"url": url, "links": links})

            if depth + 1 <= self.max_depth:
                for link in links:
                    if link not in seen:
                        queue.append((link, depth + 1))

        return results

    def _extract_inbounds(self, base_url: str, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        out: List[str] = []
        for a in soup.find_all("a", href=True):
            norm = normalise_url(base_url, a["href"])
            if not norm:
                continue
            if not same_subdomain(norm, self.root_netloc):
                continue
            out.append(norm)
        # de-dupe while preserving order
        uniq: List[str] = []
        seen: Set[str] = set()
        for u in out:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        return uniq
