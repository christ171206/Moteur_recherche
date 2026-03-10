import logging
from datetime import datetime
from typing import List, Dict, Tuple
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Document:
    """Modèle de document"""
    def __init__(self, id: int, titre: str, description: str, contenu: str, 
                 categorie: str, tags: str, auteur: str, date_publication: str,
                 url: str = None, vue: int = 0, pertinence_score: float = 0,
                 views_count: int = 0, **kwargs):
        """Initialise un document - accepte les kwargs pour la compatibilité BD"""
        self.id = id
        self.titre = titre
        self.description = description
        self.contenu = contenu
        self.categorie = categorie
        self.tags = tags.split(',') if tags else []
        self.auteur = auteur
        self.date_publication = date_publication
        self.url = url
        self.views_count = views_count or vue  # Support vue ou views_count
        self.relevance_score = pertinence_score
        # Ignorer les arguments supplémentaires (date_creation, etc.)
        self.vue = vue

    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'contenu': self.contenu[:200] + '...' if len(self.contenu) > 200 else self.contenu,
            'categorie': self.categorie,
            'tags': self.tags,
            'auteur': self.auteur,
            'date_publication': self.date_publication,
            'views_count': self.views_count,
            'relevance_score': round(self.relevance_score, 4) if self.relevance_score else 0,
            'url': self.url
        }

class SearchQuery:
    """Représente une requête de recherche"""
    def __init__(self, query: str, filters: Dict = None):
        self.query = query.strip().lower()
        self.filters = filters or {}
        self.timestamp = datetime.now()
        
    def get_terms(self) -> List[str]:
        """Extrait les termes de la requête"""
        return [term.strip() for term in self.query.split() if len(term) > 2]

class SearchResult:
    """Représente les résultats de recherche"""
    def __init__(self, query: str, documents: List[Document], 
                 total: int, duration_ms: float):
        self.query = query
        self.documents = documents
        self.results = documents  # Alias pour compatibilité
        self.total = total
        self.total_results = total  # Alias pour compatibilité
        self.duration_ms = duration_ms
        self.search_time = duration_ms / 1000.0  # Convertir en secondes
        
    def to_dict(self):
        return {
            'query': self.query,
            'total_results': self.total_results,
            'results': [doc.to_dict() for doc in self.documents],
            'search_time': self.search_time
        }
