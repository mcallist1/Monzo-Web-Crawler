from crawler.crawler import SequentialCrawler
from crawler.url_utils import canonicalize_start

class TestFetcher:
    """Fake fetcher: returns HTML bodies from a dict; 200 for hits, 404 otherwise."""
    def __init__(self, pages, ctype='text/html'):
        self.pages = pages
        self.ctype = ctype

    def fetch(self, url: str):
        body = self.pages.get(url, '')
        status = 200 if body else 404
        if isinstance(body, tuple): # just here for the 'test_skips_non_html_pages' test
            return body
        return status, body, self.ctype

def test_sequential_crawl_stays_in_same_subdomain_and_expands_links():
    start = "https://example.com/"
    # A tiny site graph:
    pages = {
        "https://example.com/": '<a href="/a">A</a> <a href="/b">B</a> <a href="https://other.com/">X</a>',
        "https://example.com/a": '<a href="/">Home</a>',
        "https://example.com/b": '<a href="/a">A</a>',
    }
    fetcher = TestFetcher(pages)

    crawler = SequentialCrawler(start_url=start, max_pages=10, fetcher=fetcher)
    results = crawler.run()  # returns list of {"url":..., "links":[...]} in visit order

    visited = [r["url"] for r in results]
    assert visited[:3] == ["https://example.com/", "https://example.com/a", "https://example.com/b"]  # order may vary after first, but this is fine for now

    # Ensure external link wasn't followed
    assert "https://other.com/" not in visited

    # Ensure links are normalized & in-bounds
    root = canonicalize_start(start)
    for r in results:
        assert r["url"].startswith("https://example.com")
        for link in r["links"]:
            assert link.startswith("https://example.com")

def test_sequential_respects_max_pages():
    start = "https://example.com/"
    pages = {start: ''.join(f'<a href="/{i}">{i}</a>' for i in range(100))}
    for i in range(100):
        pages[f"https://example.com/{i}"] = ""

    fetcher = TestFetcher(pages)
    crawler = SequentialCrawler(start_url=start, max_pages=5, fetcher=fetcher)
    results = crawler.run()
    assert len(results) <= 5

def test_respects_max_depth_zero():
    pages = {
        "https://example.com/": '<a href="/a">A</a><a href="/b">B</a>',
        "https://example.com/a": "",
        "https://example.com/b": "",
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10, max_depth=0)
    results = c.run()
    assert [r["url"] for r in results] == ["https://example.com/"]

def test_skips_non_html_pages():
    pages = {
        "https://example.com/": '<a href="/pdf">pdf</a>',
        "https://example.com/pdf": (200, "%PDF-1.4 ...", "application/pdf"),
    }

    fetcher = TestFetcher(pages)
    c = SequentialCrawler(start_url="https://example.com/", max_pages=5, fetcher=fetcher,)
    results = c.run()
    # two visits: / then /pdf; /pdf yields no links because it's non-HTML
    assert any(r["url"].endswith("/") for r in results)
    assert any(r["url"].endswith("/pdf") and r["links"] == [] for r in results)

def test_no_revisit_when_multiple_pages_link_to_same_url():
    pages = {
        "https://example.com/": '<a href="/a">A</a><a href="/b">B</a>',
        "https://example.com/a": '<a href="/c">C</a>',
        "https://example.com/b": '<a href="/c">C</a>',
        "https://example.com/c": "",
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10, max_depth=5)
    results = c.run()
    urls = [r["url"] for r in results]
    assert urls.count("https://example.com/c") == 1

def test_non_200_status_yields_no_links():
    pages = {
        "https://example.com/": '<a href="/bad">bad</a>',
        "https://example.com/bad": (500, "oops", "text/html"),
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10)
    results = c.run()
    by_url = {r["url"]: r for r in results}
    assert by_url["https://example.com/bad"]["links"] == []

def test_external_links_ignored():
    pages = {
        "https://example.com/": '<a href="https://other.com/x">X</a><a href="/in">In</a>',
        "https://example.com/in": "",
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10)
    results = c.run()
    root = next(r for r in results if r["url"] == "https://example.com/")
    assert root["links"] == ["https://example.com/in"]
    visited = [r["url"] for r in results]
    assert "https://other.com/x" not in visited

def test_normalization_and_dedupe_preserves_order():
    pages = {
        "https://example.com/": (
            '<a href="/a#frag">A1</a>'
            '<a href="/a">A2</a>'
            '<a href="./a">A3</a>'
            '<a href="/b//c">BC</a>'
        ),
        "https://example.com/a": "",
        "https://example.com/b/c": "",
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10)
    results = c.run()
    root = next(r for r in results if r["url"] == "https://example.com/")
    # Expect collapsed unique links, sorted (since you sort before storing)
    assert root["links"] == ["https://example.com/a", "https://example.com/b/c"]

def test_ignores_non_http_schemes():
    pages = {
        "https://example.com/": '<a href="mailto:x@y.com">m</a><a href="javascript:alert(1)">js</a>',
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10)
    results = c.run()
    assert results[0]["links"] == []

def test_visit_order_is_bfs_with_sorted_links():
    pages = {
        "https://example.com/": '<a href="/b">B</a><a href="/a">A</a>',  # discovered unsorted
        "https://example.com/a": "",
        "https://example.com/b": "",
    }
    c = SequentialCrawler("https://example.com/", TestFetcher(pages), max_pages=10)
    results = c.run()
    assert [r["url"] for r in results] == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
    ]

def test_root_non_html_yields_no_links_and_stops():
    start = "https://example.com/"
    pages = {start: "BINARY"}
    fetcher = TestFetcher(pages, ctype="application/pdf")
    c = SequentialCrawler(start, fetcher, max_pages=10)
    assert c.run() == [{"url": start, "links": []}]
