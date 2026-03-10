#!/usr/bin/env python
"""Debug script pour vérifier les données"""

import sys
sys.path.insert(0, '.')

from services import DatabaseService, SearchService

print("\n" + "="*60)
print("DEBUG: Vérification des données")
print("="*60 + "\n")

# 1. Vérifier les documents en BD
print("1️⃣  Documents en base de données:")
try:
    all_docs = DatabaseService.get_all_documents()
    print(f"   Total: {len(all_docs)} documents\n")
    for doc in all_docs[:10]:
        print(f"   [{doc.id:2d}] {doc.titre}")
except Exception as e:
    print(f"   Erreur: {e}")

# 2. Tester une recherche simple
print("\n2️⃣  Test de recherche 'Python':")
try:
    result = SearchService.search("Python", {}, 5)
    print(f"   Résultats: {result.total_results}")
    print(f"   Temps: {result.search_time:.3f}s\n")
    for r in result.results[:3]:
        print(f"   • {r.titre} (relevance: {r.relevance_score:.2f})")
except Exception as e:
    print(f"   Erreur: {e}")

# 3. Tester recherche Web
print("\n3️⃣  Test de recherche 'Web':")
try:
    result = SearchService.search("Web", {}, 5)
    print(f"   Résultats: {result.total_results}")
    print(f"   Temps: {result.search_time:.3f}s\n")
    for r in result.results[:3]:
        print(f"   • {r.titre} (relevance: {r.relevance_score:.2f})")
except Exception as e:
    print(f"   Erreur: {e}")

# 4. Statistiques
print("\n4️⃣  Statistiques:")
try:
    stats = SearchService.get_statistics()
    print(f"   Requêtes totales: {stats.get('total_queries', 0)}")
    print(f"   Documents: {len(all_docs)}")
except Exception as e:
    print(f"   Erreur: {e}")

print("\n" + "="*60)
print("✅ Debug terminé!")
print("="*60 + "\n")
