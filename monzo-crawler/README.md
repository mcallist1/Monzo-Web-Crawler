# Monzo Crawler

A simple, single-subdomain web crawler implemented in Python.  
Given a starting URL, it visits each page on the same subdomain, extracts links, and prints the crawl results.

---

## Features
- Sequential breadth-first crawl
- Enforces same-subdomain scope
- Skips non-HTML content
- Returns normalized, absolute URLs
- Configurable max pages and depth
- Pluggable fetchers (test vs real HTTP)

---

## Requirements
- Python 3.10+ (tested with 3.13)
- Dependencies:
  - [requests](https://docs.python-requests.org/)  
  - [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)

Install them with:

```
pip install -r requirements.txt
```

## Usage

Run from the command line:


  python main.py https://monzo.com/ --max-pages 20 --max-depth 2


---

## Tests

This project uses [pytest](https://docs.pytest.org/) for testing.

To install pytest and run the suite from the project root:
```
pip install pytest
pytest -q
```

## Testing strategy

Unit tests use a tiny in-memory fetcher (DictFetcher) that simulates the network with a Python dict: URL -> (status, body, content_type).

This makes tests deterministic, fast, and isolated (no external calls).

It lets us model edge cases (non-HTML, duplicates, depth/limit caps) precisely.

The production HTTP client is RequestsFetcher, but we only use it for optional integration checks.

By default, the test suite does not hit the network.

You can enable a sample network test with pytest -m "slow and network" (see pytest.ini).

This approach exercises the crawler’s logic (scope limiting, traversal order, normalization, dedupe) without the flakiness and ethics concerns of crawling real sites during testing.

