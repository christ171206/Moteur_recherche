import logging
import mysql.connector
import math
import time
from typing import List, Dict, Tuple
from collections import Counter
import re
from config import MYSQL_CONFIG
from models import Document, SearchQuery, SearchResult

logger = logging.getLogger(__name__)

# =====================================================
# DATABASE SERVICE
# =====================================================
class DatabaseService:
    """Gère les opérations avec la base de données MySQL"""
    
    @staticmethod
    def get_connection():
        """Crée une connexion à la BD"""
        try:
            return mysql.connector.connect(**MYSQL_CONFIG)
        except mysql.connector.Error as err:
            logger.error(f"Erreur BD: {err}")
            raise

    @staticmethod
    def add_document(titre: str, description: str, contenu: str, 
                     categorie: str, tags: str, auteur: str, 
                     url: str = None, date_publication: str = None) -> int:
        """Ajoute un nouveau document"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO documents 
                (titre, description, contenu, categorie, tags, auteur, url, date_publication)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (titre, description, contenu, categorie, tags, auteur, url, date_publication))
            conn.commit()
            doc_id = cursor.lastrowid
            
            logger.info(f"Document ajouté: ID={doc_id}")
            cursor.close()
            conn.close()
            return doc_id
        except Exception as e:
            logger.error(f"Erreur ajout document: {e}")
            raise

    @staticmethod
    def get_all_documents() -> List[Document]:
        """Récupère tous les documents actifs"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM documents WHERE active = TRUE ORDER BY date_creation DESC"
            cursor.execute(query)
            docs = cursor.fetchall()
            
            documents = [Document(**doc) for doc in docs]
            cursor.close()
            conn.close()
            return documents
        except Exception as e:
            logger.error(f"Erreur récupération documents: {e}")
            raise

    @staticmethod
    def get_document_by_id(doc_id: int) -> Document:
        """Récupère un document par son ID"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM documents WHERE id = %s AND active = TRUE", (doc_id,))
            doc = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if doc:
                return Document(**doc)
            return None
        except Exception as e:
            logger.error(f"Erreur récupération document: {e}")
            raise

    @staticmethod
    def delete_document(doc_id: int) -> bool:
        """Supprime un document (soft delete)"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE documents SET active = FALSE WHERE id = %s", (doc_id,))
            conn.commit()
            
            logger.info(f"Document supprimé: ID={doc_id}")
            cursor.close()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erreur suppression document: {e}")
            raise

    @staticmethod
    def increment_views(doc_id: int, query: str = None):
        """Enregistre une vue de document"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE documents SET vue = vue + 1 WHERE id = %s",
                (doc_id,)
            )
            
            cursor.execute(
                "INSERT INTO document_views (document_id, user_query) VALUES (%s, %s)",
                (doc_id, query)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Erreur enregistrement vue: {e}")

    @staticmethod
    def save_search_stats(query_text: str, nb_resultats: int, 
                         document_clicked: int = None, duree_ms: float = 0):
        """Enregistre les statistiques de recherche"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO search_stats (query_text, nb_resultats, document_clicked, duree_requete_ms)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (query_text, nb_resultats, document_clicked, int(duree_ms)))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Erreur enregistrement stats: {e}")

    @staticmethod
    def get_trending_queries(limit: int = 10) -> List[Dict]:
        """Récupère les requêtes les plus populaires"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT query_text, COUNT(*) as nb_recherches, 
                       AVG(nb_resultats) as avg_resultats
                FROM search_stats
                WHERE query_text IS NOT NULL
                GROUP BY query_text
                ORDER BY nb_recherches DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Erreur récupération tendances: {e}")
            return []


# =====================================================
# TF-IDF SERVICE
# =====================================================
class TFIDFService:
    """Implémente l'algorithme TF-IDF pour le ranking"""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize un texte en termes"""
        # Convertir en minuscules et supprimer la ponctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        # Diviser en mots et filtrer les vides
        tokens = [word for word in text.split() if len(word) > 2]
        return tokens

    @staticmethod
    def calculate_tf(term: str, tokens: List[str]) -> float:
        """Calcule Term Frequency"""
        return tokens.count(term.lower()) / len(tokens) if tokens else 0

    @staticmethod
    def calculate_idf(term: str, documents: List[Document]) -> float:
        """Calcule Inverse Document Frequency"""
        count_docs_with_term = sum(
            1 for doc in documents 
            if term.lower() in TFIDFService.tokenize(doc.titre + ' ' + doc.contenu)
        )
        if count_docs_with_term == 0:
            return 0
        return math.log(len(documents) / count_docs_with_term)

    @staticmethod
    def calculate_tfidf_score(document: Document, query_terms: List[str], 
                             all_documents: List[Document]) -> float:
        """Calcule le score TF-IDF d'un document pour une requête"""
        doc_tokens = TFIDFService.tokenize(document.titre + ' ' + document.description + ' ' + document.contenu)
        
        score = 0
        for term in query_terms:
            tf = TFIDFService.calculate_tf(term, doc_tokens)
            idf = TFIDFService.calculate_idf(term, all_documents)
            score += tf * idf
        
        return score

    @staticmethod
    def rank_documents(documents: List[Document], query_terms: List[str], 
                      all_documents: List[Document] = None) -> List[Document]:
        """Classe les documents selon TF-IDF"""
        if all_documents is None:
            all_documents = documents
        
        for doc in documents:
            doc.pertinence_score = TFIDFService.calculate_tfidf_score(doc, query_terms, all_documents)
        
        # Trier par pertinence décroissante
        documents.sort(key=lambda d: d.pertinence_score, reverse=True)
        return documents


# =====================================================
# SEARCH SERVICE
# =====================================================
class SearchService:
    """Gère les opérations de recherche"""
    
    @staticmethod
    def search(query_text: str, filters: Dict = None, limit: int = 20) -> SearchResult:
        """Effectue une recherche"""
        start_time = time.time()
        
        try:
            # Parser la requête
            search_query = SearchQuery(query_text, filters)
            query_terms = search_query.get_terms()
            
            if not query_terms:
                return SearchResult(query_text, [], 0, 0)
            
            # Récupérer tous les documents
            all_docs = DatabaseService.get_all_documents()
            
            # Filtrer par terme (FULLTEXT SEARCH)
            relevant_docs = SearchService._filter_documents(all_docs, query_terms)
            
            # Appliquer les filtres supplémentaires
            if filters:
                relevant_docs = SearchService._apply_filters(relevant_docs, filters)
            
            # Classer les résultats avec TF-IDF
            ranked_docs = TFIDFService.rank_documents(relevant_docs, query_terms, all_docs)
            
            # Limiter le nombre de résultats
            results = ranked_docs[:limit]
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Enregistrer les statistiques
            DatabaseService.save_search_stats(query_text, len(results), duree_ms=duration_ms)
            
            logger.info(f"Recherche: '{query_text}' → {len(results)} résultats en {duration_ms:.2f}ms")
            
            search_result = SearchResult(query_text, results, len(all_docs), duration_ms)
            return search_result
            
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return SearchResult(query_text, [], 0, (time.time() - start_time) * 1000)

    @staticmethod
    def _filter_documents(documents: List[Document], query_terms: List[str]) -> List[Document]:
        """Filtre les documents pertinents pour les termes"""
        relevant = []
        
        for doc in documents:
            # Vérifier si le document contient au moins un terme
            doc_text = (doc.titre + ' ' + doc.description + ' ' + doc.contenu).lower()
            if any(term in doc_text for term in query_terms):
                relevant.append(doc)
        
        return relevant

    @staticmethod
    def _apply_filters(documents: List[Document], filters: Dict) -> List[Document]:
        """Applique les filtres de recherche avancée"""
        filtered = documents
        
        # Filtre par catégorie
        if 'categorie' in filters and filters['categorie']:
            filtered = [d for d in filtered if d.categorie.lower() == filters['categorie'].lower()]
        
        # Filtre par tags
        if 'tags' in filters and filters['tags']:
            filter_tags = filters['tags'].split(',') if isinstance(filters['tags'], str) else filters['tags']
            filtered = [d for d in filtered if any(tag in d.tags for tag in filter_tags)]
        
        # Filtre par date
        if 'date_from' in filters and filters['date_from']:
            filtered = [d for d in filtered if d.date_publication >= filters['date_from']]
        
        if 'date_to' in filters and filters['date_to']:
            filtered = [d for d in filtered if d.date_publication <= filters['date_to']]
        
        # Filtre par auteur
        if 'auteur' in filters and filters['auteur']:
            filtered = [d for d in filtered if d.auteur.lower() == filters['auteur'].lower()]
        
        return filtered

    @staticmethod
    def get_suggestions(partial_query: str) -> List[str]:
        """Retourne des suggestions d'autocomplétion"""
        try:
            # Récupérer les requêtes populaires
            trending = DatabaseService.get_trending_queries(limit=50)
            
            # Filtrer celles qui commencent par la requête partielle
            suggestions = [
                item['query_text'] for item in trending
                if item['query_text'].lower().startswith(partial_query.lower())
            ]
            
            return suggestions[:10]  # Limiter à 10 suggestions
        except Exception as e:
            logger.error(f"Erreur suggestions: {e}")
            return []

    @staticmethod
    def get_statistics() -> Dict:
        """Retourne des statistiques générales"""
        try:
            all_docs = DatabaseService.get_all_documents()
            trending = DatabaseService.get_trending_queries(limit=10)
            
            total_views = sum(doc.vue for doc in all_docs)
            
            return {
                'total_documents': len(all_docs),
                'total_vues': total_views,
                'categories': list(set(doc.categorie for doc in all_docs)),
                'tendances': trending
            }
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
            return {}
