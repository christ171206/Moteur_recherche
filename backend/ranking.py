import logging
import math
from typing import List, Dict, Tuple
from collections import Counter
import re

logger = logging.getLogger(__name__)

class BM25Ranker:
    """
    Implémente l'algorithme BM25 (meilleur que TF-IDF)
    Utilisé par Google et tous les moteurs modernes
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialise BM25
        
        k1: Contrôle la saturation du terme (default: 1.5)
        b: Contrôle l'effet de la longueur du document (default: 0.75)
        """
        self.k1 = k1
        self.b = b
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize le texte"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = [word for word in text.split() if len(word) > 2]
        return tokens
    
    def calculate_bm25(self, documents: List[dict], query_terms: List[str]) -> List[Tuple[int, float]]:
        """
        Calcule le score BM25 pour chaque document
        
        Returns:
            [(doc_id, score), ...]
        """
        # Longueur moyenne des documents
        doc_lengths = [len(self.tokenize(doc['contenu'])) for doc in documents]
        if not doc_lengths:
            return []
        
        avg_doc_length = sum(doc_lengths) / len(doc_lengths)
        
        # Nombre total de documents
        N = len(documents)
        
        scores = []
        
        for idx, doc in enumerate(documents):
            doc_tokens = self.tokenize(doc['titre'] + ' ' + doc['description'] + ' ' + doc['contenu'])
            doc_length = len(doc_tokens)
            token_counts = Counter(doc_tokens)
            
            score = 0
            
            for term in query_terms:
                # Nombre de docs contenant ce terme
                docs_with_term = sum(
                    1 for d in documents 
                    if term.lower() in self.tokenize(d['titre'] + ' ' + d['contenu'])
                )
                
                if docs_with_term == 0:
                    continue
                
                # IDF
                idf = math.log((N - docs_with_term + 0.5) / (docs_with_term + 0.5) + 1)
                
                # Term frequency dans le doc
                tf = token_counts.get(term.lower(), 0)
                
                # Formule BM25
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_doc_length))
                
                score += idf * (numerator / denominator)
            
            scores.append((doc['id'], score, idx))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)


class PageRankCalculator:
    """
    Calcule le PageRank simplifié pour favoriser les pages populaires
    """
    
    @staticmethod
    def calculate_pagerank(documents: List[dict], links_map: Dict[int, List[int]], 
                         iterations: int = 10, damping_factor: float = 0.85) -> Dict[int, float]:
        """
        Calcule le PageRank pour chaque document
        
        Args:
            documents: Liste des documents
            links_map: {doc_id: [doc_ids qu'il pointe vers]}
            iterations: Nombre de itérations
            damping_factor: Facteur d'amortissement (0.85 = Google)
        
        Returns:
            {doc_id: pagerank_score}
        """
        N = len(documents)
        if N == 0:
            return {}
        
        # Initialiser tous les PageRanks à 1/N
        pagerank = {doc['id']: 1.0 / N for doc in documents}
        
        # Itérer
        for _ in range(iterations):
            new_pagerank = {}
            
            for doc in documents:
                doc_id = doc['id']
                rank = (1 - damping_factor) / N
                
                # Trouver les documents qui pointent vers celui-ci
                for source_id, targets in links_map.items():
                    if doc_id in targets:
                        num_outlinks = len(targets)
                        if num_outlinks > 0:
                            rank += damping_factor * pagerank[source_id] / num_outlinks
                
                new_pagerank[doc_id] = rank
            
            pagerank = new_pagerank
        
        return pagerank


class AdvancedRanker:
    """
    Combine BM25 + PageRank + Signals additionnels
    pour un ranking Google-like
    """
    
    def __init__(self):
        self.bm25 = BM25Ranker()
        self.pagerank_calc = PageRankCalculator()
    
    def rank_documents(self, documents: List[dict], query_terms: List[str],
                      links_map: Dict[int, List[int]] = None,
                      boost_factors: Dict[str, float] = None) -> List[dict]:
        """
        Classe les documents avec multiple signaux
        
        Args:
            documents: Documents à classer
            query_terms: Termes de la requête
            links_map: Graphe de liens (pour PageRank)
            boost_factors: {field: factor} pour booster certains champs
        
        Returns:
            Documents classés avec scores détaillés
        """
        if not documents:
            return []
        
        # Signaux par défaut
        if boost_factors is None:
            boost_factors = {
                'titre': 3.0,      # Titre = 3x plus important
                'categorie': 1.5,  # Catégorie = 1.5x
                'view_count': 1.1  # Pages vues = petit boost
            }
        
        # 1. Score BM25
        bm25_scores = self.bm25.calculate_bm25(documents, query_terms)
        bm25_map = {doc_id: score for doc_id, score, _ in bm25_scores}
        
        # Normaliser BM25 [0-1]
        max_bm25 = max(bm25_map.values()) if bm25_map else 1
        for doc_id in bm25_map:
            bm25_map[doc_id] = bm25_map[doc_id] / max_bm25 if max_bm25 > 0 else 0
        
        # 2. Score PageRank (si links_map fourni)
        if links_map:
            pagerank = self.pagerank_calc.calculate_pagerank(documents, links_map)
            max_pr = max(pagerank.values()) if pagerank else 1
            pagerank = {doc_id: score / max_pr for doc_id, score in pagerank.items()}
        else:
            pagerank = {doc['id']: 0.5 for doc in documents}
        
        # 3. Score de pertinence des champs
        field_scores = {}
        for doc in documents:
            doc_id = doc['id']
            score = 0
            
            # Score basé sur occurrence dans titre
            titre_tokens = self.bm25.tokenize(doc['titre'])
            titre_matches = sum(1 for term in query_terms if term in titre_tokens)
            score += titre_matches * boost_factors['titre']
            
            # Catégorie match
            if any(term in doc.get('categorie', '').lower() for term in query_terms):
                score += boost_factors['categorie']
            
            # Boost pour vues
            view_count = doc.get('vue', 0)
            score += math.log(view_count + 1) * boost_factors['view_count']
            
            field_scores[doc_id] = score
        
        # Normaliser field scores
        max_field = max(field_scores.values()) if field_scores else 1
        for doc_id in field_scores:
            field_scores[doc_id] = field_scores[doc_id] / max_field if max_field > 0 else 0
        
        # 4. Score final = combination pondérée
        weights = {
            'bm25': 0.5,        # 50% BM25
            'pagerank': 0.2,    # 20% PageRank
            'fields': 0.3       # 30% Pertinence champs
        }
        
        final_scores = {}
        for doc in documents:
            doc_id = doc['id']
            final_scores[doc_id] = (
                weights['bm25'] * bm25_map.get(doc_id, 0) +
                weights['pagerank'] * pagerank.get(doc_id, 0) +
                weights['fields'] * field_scores.get(doc_id, 0)
            )
        
        # 5. Trier et retourner
        ranked = []
        for doc in documents:
            ranked.append({
                **doc,
                'score': final_scores[doc['id']],
                'bm25_score': bm25_map.get(doc['id'], 0),
                'pagerank_score': pagerank.get(doc['id'], 0),
                'field_score': field_scores.get(doc['id'], 0)
            })
        
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked
