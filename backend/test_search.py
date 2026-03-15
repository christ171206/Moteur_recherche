#!/usr/bin/env python3
"""
Script de test pour vérifier que la recherche fonctionne
"""

import requests
import json

API_BASE = 'http://localhost:5000/api'

def test_search():
    """Teste la fonctionnalité de recherche"""

    test_queries = [
        'python',
        'mysql',
        'flask',
        'docker',
        'machine learning'
    ]

    print("🧪 Test de l'API de recherche...\n")

    for query in test_queries:
        try:
            response = requests.get(f"{API_BASE}/search", params={'q': query, 'limit': 5})
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ '{query}' → {len(results)} résultats")
                if results:
                    print(f"   📄 Premier résultat: {results[0]['titre'][:50]}...")
            else:
                print(f"❌ '{query}' → Erreur {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ '{query}' → Exception: {e}")

        print()

def test_health():
    """Teste le health check"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check: {e}")

if __name__ == "__main__":
    test_health()
    test_search()