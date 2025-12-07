from crawler.url_utils import normalise_url, same_subdomain, canonicalize_start

def test_normalise_simple_absolute_url():
    # First baby step: absolute URL should come back unchanged.
    assert normalise_url("https://example.com/", "https://example.com/about") == "https://example.com/about"

def test_normalise_resolves_relative_and_strips_fragment():
    base = "https://example.com/blog/"
    assert normalise_url(base, "about#team") == "https://example.com/blog/about"

def test_normalise_removes_default_ports_and_collapses_slashes():
    base = "http://a.com/"
    # Expectation:
    # - ":80" should be removed (default for http)
    # - duplicate slashes "//x//y" collapsed to "/x/y"
    assert normalise_url(base, "http://a.com:80//x//y") == "http://a.com/x/y"

def test_same_subdomain_exact_match_only():
    root = "example.com"
    assert same_subdomain("https://example.com/a", root) is True
    assert same_subdomain("https://sub.example.com/a", root) is False
    assert same_subdomain("https://other.com/a", root) is False

def test_canonicalize_start_lowercase_and_root_slash():
    assert canonicalize_start("https://Example.com") == "https://example.com/"