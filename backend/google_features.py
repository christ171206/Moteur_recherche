import logging
from typing import List, Dict
import re
from difflib import SequenceMatcher
from collections import Counter

logger = logging.getLogger(__name__)

class GoogleLikeFeatures:
    """
    Implémente les features de Google :
    - Suggestions (did you mean)
    - Featured snippets
    - Related searches
    - Search shortcuts
    """
    
    @staticmethod
    def correct_spelling(query: str, popular_queries: List[str], threshold: float = 0.8) -> Dict:
        """
        Propose des corrections orthographiques
        
        Returns:
            {
                'original': 'pythno',
                'suggestion': 'python',
                'confidence': 0.95,
                'did_you_mean': True
            }
        """
        query_lower = query.lower()
        
        # Vérifier si une requête populaire est très similaire
        best_match = None
        best_ratio = 0
        
        for popular in popular_queries:
            ratio = SequenceMatcher(None, query_lower, popular.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = popular
        
        if best_ratio >= threshold and best_match and best_match.lower() != query_lower:
            return {
                'original': query,
                'suggestion': best_match,
                'confidence': round(best_ratio, 2),
                'did_you_mean': True
            }
        
        return {
            'original': query,
            'suggestion': None,
            'confidence': 1.0,
            'did_you_mean': False
        }
    
    @staticmethod
    def extract_featured_snippet(document: Dict, query_terms: List[str]) -> Dict:
        """
        Extrait un featured snippet (réponse directe)
        du cokntenu du document
        
        Returns:
            {
                'text': '...',
                'source': 'titre du doc',
                'url': '...'
            }
        """
        content = document.get('contenu', '')
        title = document.get('titre', '')
        url = document.get('url', '')
        
        # Chercher un paragraphe contenant au moins 2 termes de requête
        paragraphs = content.split('. ')
        
        for para in paragraphs:
            query_matches = sum(1 for term in query_terms if term.lower() in para.lower())
            
            if query_matches >= min(2, len(query_terms)):
                # Limiter à 200 caractères
                snippet = para.strip()
                if len(snippet) > 200:
                    snippet = snippet[:200].rsplit(' ', 1)[0] + '...'
                
                return {
                    'text': snippet,
                    'source': title,
                    'url': url,
                    'doc_id': document.get('id')
                }
        
        return None
    
    @staticmethod
    def get_related_searches(query: str, documents: List[Dict], 
                            limit: int = 8) -> List[str]:
        """
        Retourne les recherches liées (comme Google)
        
        Basé sur :
        - Tags des résultats
        - Titres des résultats
        - Autres recherches populaires
        """
        related = set()
        
        # Extraire des tags et titres
        for doc in documents[:10]:  # Regarder top 10
            tags = doc.get('tags', [])
            if isinstance(tags, str):
                tags = tags.split(',')
            
            related.update(tag.strip() for tag in tags if tag.strip())
            
            # Extraire des mots-clés du titre
            title_words = doc.get('titre', '').split()
            related.update(word.lower() for word in title_words 
                          if len(word) > 3 and word.lower() != query.lower())
        
        # Convertir en liste et trier par pertinence
        related_list = list(related)[:limit]
        return related_list
    
    @staticmethod
    def calculate_result_count(documents: List[Dict]) -> Dict:
        """
        Retourne le nombre approximatif de résultats
        "About 1,234,567 results (0.42 seconds)"
        """
        count = len(documents)
        
        # Approcher le nombre comme Google fait (plus impressionnant)
        if count > 0:
            # Multiplier par un facteur pour simuler un grand corpus
            approx_count = count * 1000  # Simulation
            
            return {
                'count': approx_count,
                'formatted': f"{approx_count:,}",
                'actual_count': count
            }
        
        return {
            'count': 0,
            'formatted': '0',
            'actual_count': 0
        }
    
    @staticmethod
    def build_search_result_item(doc: Dict, snippet: str = None,
                                featured: bool = False) -> Dict:
        """
        Construit un item de résultat formaté comme Google
        """
        result = {
            'id': doc.get('id'),
            'title': doc.get('titre', 'Sans titre'),
            'url': doc.get('url', ''),
            'display_url': GoogleLikeFeatures._format_url(doc.get('url', '')),
            'snippet': snippet or doc.get('description', '')[:160],
            'domain': GoogleLikeFeatures._extract_domain(doc.get('url', '')),
            'views': doc.get('vue', 0),
            'date': doc.get('date_publication'),
            'featured_snippet': featured,
            'score': doc.get('score', 0)
        }
        
        return result
    
    @staticmethod
    def _format_url(url: str) -> str:
        """Formate l'URL pour l'affichage (comme Google)"""
        if not url:
            return ''
        
        # Supprimer https://www.
        display = url.replace('https://', '').replace('http://', '')
        display = display.replace('www.', '')
        
        # Limiter à 60 caractères
        if len(display) > 60:
            display = display[:60] + '...'
        
        return display
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extrait le domaine"""
        if not url:
            return ''
        
        domain = url.replace('https://', '').replace('http://', '')
        domain = domain.split('/')[0].replace('www.', '')
        return domain
    
    @staticmethod
    def apply_query_filters(query: str) -> Dict:
        """
        Parse les filtres cachés dans la requête Google-like
        
        Examples:
        - "python site:github.com"
        - "machine learning filetype:pdf"
        - "deep learning -gpu"
        """
        filters = {
            'keywords': [],
            'site': None,
            'filetype': None,
            'exclude': [],
            'exact_phrase': None
        }
        
        # Exact phrase
        exact_match = re.search(r'"([^"]+)"', query)
        if exact_match:
            filters['exact_phrase'] = exact_match.group(1)
            query = query.replace(f'"{exact_match.group(1)}"', '')
        
        # Site filter
        site_match = re.search(r'site:(\S+)', query)
        if site_match:
            filters['site'] = site_match.group(1)
            query = query.replace(f'site:{site_match.group(1)}', '')
        
        # Filetype filter
        filetype_match = re.search(r'filetype:(\w+)', query)
        if filetype_match:
            filters['filetype'] = filetype_match.group(1)
            query = query.replace(f'filetype:{filetype_match.group(1)}', '')
        
        # Exclusions
        exclude_words = re.findall(r'-(\S+)', query)
        if exclude_words:
            filters['exclude'] = exclude_words
            for word in exclude_words:
                query = query.replace(f'-{word}', '')
        
        # Keywords restants
        filters['keywords'] = [w for w in query.split() if w.strip()]
        
        return filters
    
    @staticmethod
    def apply_knowledge_graph_enrichment(doc: Dict) -> Dict:
        """
        Enrichit un résultat avec des infos Knowledge Graph style
        """
        enriched = doc.copy()
        
        # Extraire des patterns simples
        if 'wikipedia' in doc.get('url', '').lower():
            enriched['source_type'] = 'Wikipedia'
            enriched['icon'] = '📖'
        elif 'github' in doc.get('url', '').lower():
            enriched['source_type'] = 'GitHub'
            enriched['icon'] = '⭐'
        elif 'stackoverflow' in doc.get('url', '').lower():
            enriched['source_type'] = 'Stack Overflow'
            enriched['icon'] = '❓'
        else:
            enriched['source_type'] = None
            enriched['icon'] = None
        
        return enriched
