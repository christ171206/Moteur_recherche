import requests
import logging
import time
from urllib.parse import urljoin, urlparse
from typing import List, Set
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class WebCrawler:
    """Web Crawler pour télécharger et explorer les pages web"""
    
    def __init__(self, max_pages: int = 50, timeout: int = 10, delay: float = 1.0):
        """
        Initialise le crawler
        
        Args:
            max_pages: Nombre max de pages à crawler
            timeout: Timeout par requête (secondes)
            delay: Délai entre les requêtes (secondes)
        """
        self.max_pages = max_pages
        self.timeout = timeout
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = []
        
        # Session avec retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # User-Agent professionnel
        self.session.headers.update({
            'User-Agent': 'SearchEngineBot/1.0 (+http://localhost:5000/bot)'
        })
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Vérifie si l'URL est valide et du même domaine"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Vérifier que c'est HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Vérifier que c'est le même domaine
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Éviter les fragments
            if '#' in url:
                url = url.split('#')[0]
            
            # Éviter les ressources non-HTML
            excluded_extensions = ['.pdf', '.zip', '.exe', '.jpg', '.png', '.gif', '.css', '.js']
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erreur validation URL {url}: {e}")
            return False
    
    def fetch_page(self, url: str) -> dict:
        """Télécharge une page web
        
        Returns:
            {
                'url': str,
                'titre': str,
                'contenu': str,
                'links': List[str],
                'status': int,
                'success': bool,
                'erreur': str (optionnel)
            }
        """
        try:
            logger.info(f"Crawling: {url}")
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            
            # Parser HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire le titre
            titre_tag = soup.find('title')
            titre = titre_tag.text.strip() if titre_tag else urlparse(url).netloc
            
            # Extraire le contenu textuel
            # Supprimer les scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            contenu = ' '.join(text.split())[:5000]  # Limiter à 5000 caractères
            
            # Extraire les liens
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                if self.is_valid_url(absolute_url, url):
                    links.append(absolute_url)
            
            return {
                'url': response.url,  # URL après redirects
                'titre': titre,
                'contenu': contenu,
                'links': list(set(links)),  # Supprimer les doublons
                'status': response.status_code,
                'success': True
            }
        
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'status': 0,
                'success': False,
                'erreur': 'Timeout'
            }
        except requests.exceptions.HTTPError as e:
            return {
                'url': url,
                'status': e.response.status_code,
                'success': False,
                'erreur': f'HTTP {e.response.status_code}'
            }
        except Exception as e:
            logger.error(f"Erreur crawling {url}: {e}")
            return {
                'url': url,
                'status': 0,
                'success': False,
                'erreur': str(e)
            }
    
    def crawl(self, seed_urls: List[str]) -> List[dict]:
        """Lance le crawl récursif
        
        Args:
            seed_urls: URLs de départ
        
        Returns:
            Liste des pages crawlées
        """
        self.to_visit = seed_urls.copy()
        pages = []
        
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop(0)
            
            # Éviter les doublons
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Crawler la page
            result = self.fetch_page(url)
            
            if result['success']:
                pages.append(result)
                
                # Ajouter les nouveaux liens à la queue
                base_domain = url
                for link in result.get('links', []):
                    if link not in self.visited_urls:
                        self.to_visit.append(link)
            else:
                logger.warning(f"Erreur crawling {url}: {result.get('erreur')}")
            
            # Respecter la politesse - délai entre requêtes
            if self.to_visit:  # Pas de délai après la dernière requête
                time.sleep(self.delay)
        
        logger.info(f"Crawl terminé: {len(pages)} pages téléchargées")
        return pages
