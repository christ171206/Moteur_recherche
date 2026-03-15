#!/usr/bin/env python3
"""
Script de test pour crawler des images et vidéos réelles
"""

from crawler import WebCrawler
from indexer import Indexer
import logging

logging.basicConfig(level=logging.INFO)

def test_media_crawling():
    """Test le crawling de médias sur une vraie page web"""

    # URLs de test (page locale servie par HTTP)
    test_urls = [
        "http://localhost:8080/test_page.html",  # Page locale avec médias
    ]

    print("🕷️ Test du crawling de médias...")
    print("URLs à crawler:", test_urls)

    # Initialiser le crawler (ignorer SSL pour les tests, timeout court)
    crawler = WebCrawler(max_pages=2, delay=0.5, timeout=5, verify_ssl=False)

    # Crawler les pages
    pages = crawler.crawl(test_urls)

    print(f"📄 {len(pages)} pages crawlées")

    # Filtrer les pages avec succès
    successful_pages = [p for p in pages if p.get('success')]

    print(f"✅ {len(successful_pages)} pages crawlées avec succès")

    # Compter les médias trouvés dans les métadonnées
    total_images = sum(p.get('metadata', {}).get('image_count', 0) for p in successful_pages)
    total_videos = sum(p.get('metadata', {}).get('video_count', 0) for p in successful_pages)

    print(f"🖼️ {total_images} images trouvées")
    print(f"🎥 {total_videos} vidéos trouvées")

    # Indexer les pages
    if successful_pages:
        print("📝 Indexation des pages...")
        result = Indexer.index_pages(successful_pages)
        print(f"✅ {result['reussis']} pages indexées")

    # Afficher quelques exemples
    for page in successful_pages[:3]:
        print(f"\n📋 Page: {page.get('url')}")
        print(f"   Titre: {page.get('titre', 'N/A')[:50]}...")
        print(f"   Catégorie: {page.get('categorie', 'N/A')}")
        if page.get('metadata', {}).get('filename'):
            print(f"   Fichier: {page['metadata']['filename']}")

    print("\n🎯 Test terminé!")
    print("Vous pouvez maintenant rechercher 'image' ou 'video' dans l'interface web.")

if __name__ == "__main__":
    test_media_crawling()