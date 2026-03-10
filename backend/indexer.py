import logging
from typing import List, Dict
from datetime import datetime
from services import DatabaseService
from models import Document

logger = logging.getLogger(__name__)

class Indexer:
    """Indexe les pages crawlées dans la base de données"""
    
    @staticmethod
    def index_pages(pages: List[dict]) -> Dict:
        """Indexe une liste de pages dans la BD
        
        Args:
            pages: Liste des pages (résultat du crawler)
        
        Returns:
            {
                'total': int,
                'reussis': int,
                'echoues': int,
                'details': List[dict]
            }
        """
        stats = {
            'total': len(pages),
            'reussis': 0,
            'echoues': 0,
            'details': []
        }
        
        for page in pages:
            try:
                if not page.get('success'):
                    stats['echoues'] += 1
                    stats['details'].append({
                        'url': page.get('url'),
                        'success': False,
                        'erreur': page.get('erreur')
                    })
                    continue
                
                # Vérifier que les champs requis existent
                titre = page.get('titre', 'Sans titre').strip()
                contenu = page.get('contenu', '').strip()
                url = page.get('url', '').strip()
                
                if not titre or not contenu:
                    stats['echoues'] += 1
                    stats['details'].append({
                        'url': url,
                        'success': False,
                        'erreur': 'Titre ou contenu manquant'
                    })
                    continue
                
                # Extraire le domaine comme catégorie
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                categorie = domain.replace('www.', '')
                
                # Ajouter à la BD
                doc_id = DatabaseService.add_document(
                    titre=titre[:255],  # Limiter VARCHAR(255)
                    description=contenu[:200],  # Première partie du contenu
                    contenu=contenu,
                    categorie=categorie,
                    tags='crawler,indexe,web',
                    auteur='WebCrawler',
                    url=url,
                    date_publication=datetime.now().date().isoformat()
                )
                
                stats['reussis'] += 1
                stats['details'].append({
                    'url': url,
                    'doc_id': doc_id,
                    'success': True,
                    'titre': titre[:50] + '...' if len(titre) > 50 else titre
                })
                
                logger.info(f"Document indexé: {doc_id} - {titre}")
            
            except Exception as e:
                logger.error(f"Erreur indexing {page.get('url')}: {e}")
                stats['echoues'] += 1
                stats['details'].append({
                    'url': page.get('url'),
                    'success': False,
                    'erreur': str(e)
                })
        
        return stats
    
    @staticmethod
    def extract_text(html: str) -> str:
        """Extrait le texte d'une page HTML
        
        Args:
            html: Contenu HTML
        
        Returns:
            Texte extrait et nettoyé
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Supprimer les scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraire le texte
            text = soup.get_text(separator=' ', strip=True)
            
            # Nettoyer les espaces multiples
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.error(f"Erreur extraction texte: {e}")
            return ""
    
    @staticmethod
    def extract_metadata(html: str, url: str) -> dict:
        """Extrait les métadonnées d'une page HTML
        
        Args:
            html: Contenu HTML
            url: URL de la page
        
        Returns:
            {
                'titre': str,
                'description': str,
                'keywords': str,
                'author': str,
                'og_title': str,
                'og_description': str,
            }
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            metadata = {}
            
            # Title tag
            title_tag = soup.find('title')
            metadata['titre'] = title_tag.text.strip() if title_tag else url
            
            # Meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            metadata['description'] = desc_tag.get('content', '') if desc_tag else ''
            
            # Meta keywords
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            metadata['keywords'] = keywords_tag.get('content', '') if keywords_tag else ''
            
            # Meta author
            author_tag = soup.find('meta', attrs={'name': 'author'})
            metadata['author'] = author_tag.get('content', '') if author_tag else 'Inconnu'
            
            # OpenGraph tags
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            metadata['og_title'] = og_title.get('content', '') if og_title else ''
            
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            metadata['og_description'] = og_desc.get('content', '') if og_desc else ''
            
            return metadata
        except Exception as e:
            logger.error(f"Erreur extraction métadonnées: {e}")
            return {}
    
    @staticmethod
    def clean_content(text: str, max_length: int = 10000) -> str:
        """Nettoie et limite le contenu
        
        Args:
            text: Texte brut
            max_length: Longueur maximale
        
        Returns:
            Texte nettoyé
        """
        # Supprimer les caractères de contrôle
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        # Supprimer les espaces multiples
        text = ' '.join(text.split())
        
        # Limiter la longueur
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text
