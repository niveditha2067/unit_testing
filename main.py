import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(str)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    if not urlparse(href).netloc:
                        href = urljoin(base_url or url, href)
                    if (base_url or url) in href:
                        self.crawl(href, base_url=base_url or url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

# ----------------- UNIT TESTS --------------------

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

class WebCrawlerTests(unittest.TestCase):

    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com", crawler.index)
        self.assertIn("https://example.com/about", crawler.visited)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com", crawler.visited)
        self.assertEqual(crawler.index.get("https://example.com"), None)

    def test_search_results(self):
        crawler = WebCrawler()
        crawler.index = {
            "https://a.com": "This page contains keyword",
            "https://b.com": "This one does not"
        }
        results = crawler.search("keyword")
        self.assertEqual(results, ["https://a.com"])

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])
        output = mock_stdout.getvalue()
        self.assertIn("Search results:", output)
        self.assertIn("- https://test.com/result", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_no_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results([])
        output = mock_stdout.getvalue()
        self.assertIn("No results found.", output)

# ----------------- EXECUTION --------------------
if __name__ == "__main__":
    unittest.main()
