import argparse
from crawler.crawler import SequentialCrawler
from crawler.fetcher import RequestsFetcher

def main():
    parser = argparse.ArgumentParser(description="Single-subdomain web crawler")
    parser.add_argument("--start_url", help="Starting URL (e.g. https://monzo.com/)")
    parser.add_argument("--max-pages", type=int, default=500)
    parser.add_argument("--max-depth", type=int, default=32)
    args = parser.parse_args()

    fetcher = RequestsFetcher()
    crawler = SequentialCrawler(
        start_url=args.start_url,
        fetcher=fetcher,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
    )
    results = crawler.run()

    for item in results:
        print(f"VISITED {item['url']}")
        links = item["links"]
        if links:
            print("LINKS:\n  " + "\n  ".join(f"- {l}" for l in links))
        else:
            print("LINKS: (none)")
        print()


if __name__ == "__main__":
    main()
