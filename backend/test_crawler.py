#!/usr/bin/env python3
"""Test script for the enhanced crawler"""

from crawler import WebCrawler
import logging

logging.basicConfig(level=logging.INFO)

def test_crawler():
    crawler = WebCrawler()

    # Test URLs for different content types
    test_urls = [
        'https://httpbin.org/html',  # HTML
        'https://httpbin.org/json',  # JSON (should be treated as web)
        # Note: For real media testing, we'd need actual URLs
        # 'https://example.com/image.jpg',  # Image
        # 'https://example.com/document.pdf',  # PDF
    ]

    for url in test_urls:
        print(f"\n=== Testing {url} ===")
        result = crawler.fetch_page(url)
        print(f"Success: {result.get('success', False)}")
        print(f"Category: {result.get('categorie', 'unknown')}")
        print(f"Title: {result.get('titre', '')[:50]}...")
        print(f"Content length: {len(result.get('contenu', ''))}")
        if 'metadata' in result and result['metadata']:
            print(f"Metadata keys: {list(result['metadata'].keys())}")

if __name__ == "__main__":
    test_crawler()