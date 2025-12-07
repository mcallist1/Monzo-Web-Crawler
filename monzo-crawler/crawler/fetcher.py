from typing import Tuple
import requests

class RequestsFetcher:
    def __init__(self, timeout: float = 10.0, user_agent: str = "monzo-crawler/0.1"):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch(self, url: str) -> Tuple[int, str, str]:
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            status = resp.status_code
            ctype = resp.headers.get("Content-Type", "")
            return status, resp.text or "", ctype or ""
        except requests.RequestException:
            return 0, "", ""
