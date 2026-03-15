#!/usr/bin/env python3
"""
Test rapide de la recherche pour vérifier la correction
"""

import requests

def test_search_fix():
    """Teste que la recherche fonctionne correctement"""

    # Test avec un terme qui existe
    response = requests.get('http://localhost:5000/api/search?q=python&limit=5')
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"✅ 'python' → {len(results)} résultats")
        print(f"   Total dans base: {data.get('total_results', 0)}")
    else:
        print(f"❌ Erreur API: {response.status_code}")

    # Test avec un terme qui n'existe pas
    response = requests.get('http://localhost:5000/api/search?q=loko&limit=5')
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"✅ 'loko' → {len(results)} résultats")
        print(f"   Total dans base: {data.get('total_results', 0)}")
    else:
        print(f"❌ Erreur API: {response.status_code}")

if __name__ == "__main__":
    test_search_fix()