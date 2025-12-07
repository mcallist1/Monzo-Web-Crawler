import re
from urllib.parse import urlparse, urlunparse, urljoin

def normalise_url(base_url: str, href: str):
    if not href:
        return None
    abs_url = urljoin(base_url, href)
    p = urlparse(abs_url)

    if p.scheme not in ("http", "https"):
        return None
    # Remove default ports
    netloc = p.netloc.lower()
    if (p.scheme == "http" and netloc.endswith(":80")) or \
        (p.scheme == "https" and netloc.endswith(":443")):
            netloc = netloc.rsplit(":", 1)[0]

    path = _collapse_slashes(p.path or "/")
    # Rebuild without changing anything else yet
    return urlunparse((p.scheme, netloc, path, "", p.query, ""))

def canonicalize_start(url: str) -> str:
    n = normalise_url(url, url)
    if n is None:
        raise ValueError(f"Invalid start URL: {url}")
    p = urlparse(n)
    path = p.path or "/"
    return urlunparse((p.scheme, p.netloc, path, "", p.query, ""))

def same_subdomain(url: str, root_netloc: str) -> bool:
    try:
        return urlparse(url).netloc.lower() == root_netloc.lower()
    except Exception:
        return False

def _collapse_slashes(path: str) -> str:
    """Replace multiple / with a single one, always ensure leading /."""
    if not path:
        return "/"
    collapsed = re.sub(r"/{2,}", "/", path)
    return collapsed if collapsed.startswith("/") else "/" + collapsed