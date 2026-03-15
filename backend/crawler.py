import requests
import logging
import time
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Set
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import re
from PIL import Image
import io
import fitz  # PyMuPDF for PDF
import json
import hashlib
import mimetypes

# Imports optionnels pour OCR et traitement vidéo
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from moviepy.editor import VideoFileClip
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

logger = logging.getLogger(__name__)

class WebCrawler:
    """Web Crawler pour télécharger et explorer les pages web"""
    
    def __init__(self, max_pages: int = 50, timeout: int = 10, delay: float = 1.0, download_dir: str = 'downloads', verify_ssl: bool = True):
        """
        Initialise le crawler
        
        Args:
            max_pages: Nombre max de pages à crawler
            timeout: Timeout par requête (secondes)
            delay: Délai entre les requêtes (secondes)
            download_dir: Dossier pour télécharger les fichiers
        """
        self.max_pages = max_pages
        self.timeout = timeout
        self.delay = delay
        self.download_dir = download_dir
        self.verify_ssl = verify_ssl
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = []
        
        # Créer le dossier de téléchargement
        os.makedirs(self.download_dir, exist_ok=True)
        
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
    
    def normalize_url(self, url: str) -> str:
        """Normalise une URL pour éviter les doublons (même base, pas de fragments, sans slash final)."""
        try:
            parsed = urlparse(url)
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            path = parsed.path or ''
            if path.endswith('/') and len(path) > 1:
                path = path.rstrip('/')
            normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ''))
            return normalized
        except Exception:
            return url

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Vérifie si l'URL est valide et du même domaine"""
        try:
            url = self.normalize_url(url)
            base_domain = self.normalize_url(base_domain)
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Vérifier que c'est HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Vérifier que c'est le même domaine
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Éviter les ressources non désirées, mais permettre médias
            excluded_extensions = ['.zip', '.exe', '.css', '.js', '.woff', '.woff2', '.ttf']
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
                                '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
                                '.pdf', '.mp3', '.wav', '.ogg']
            
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in excluded_extensions):
                return False
            
            # Permettre explicitement les extensions média
            if any(path_lower.endswith(ext) for ext in allowed_extensions):
                return True
            
            # Pour les URLs sans extension, vérifier si c'est probablement du contenu web
            if '.' not in parsed.path.split('/')[-1]:
                return True
            
            return True
        except Exception as e:
            logger.error(f"Erreur validation URL {url}: {e}")
            return False
    
    def fetch_page(self, url: str) -> dict:
        """Télécharge une page web ou média
        
        Returns:
            {
                'url': str,
                'titre': str,
                'contenu': str,
                'links': List[str],
                'status': int,
                'success': bool,
                'categorie': str,
                'metadata': dict,
                'erreur': str (optionnel)
            }
        """
        try:
            logger.info(f"Crawling: {url}")
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            categorie = 'web'
            metadata = {}
            contenu = ''
            titre = urlparse(url).netloc
            links = []
            
            if 'text/html' in content_type:
                # HTML page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                titre_tag = soup.find('title')
                titre = titre_tag.text.strip() if titre_tag else titre
                
                # Extract SEO metadata
                metadata = self.extract_seo_metadata(soup)
                
                # Extract content
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator=' ', strip=True)
                contenu = ' '.join(text.split())[:5000]
                
                # Extract links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    normalized_link = self.normalize_url(absolute_url)
                    if self.is_valid_url(normalized_link, url):
                        links.append(normalized_link)
                
                # Analyse des images et vidéos
                media_info = self.analyze_media(soup, url)
                contenu += ' ' + media_info.get('media', '')
                metadata.update(media_info)
                
                # Déterminer la catégorie basée sur le contenu média
                image_count = media_info.get('image_count', 0)
                video_count = media_info.get('video_count', 0)
                if video_count > 0:
                    categorie = 'video'
                elif image_count > 0:
                    categorie = 'image'
                else:
                    categorie = 'web'
                
            elif 'application/json' in content_type or 'application/javascript' in content_type or 'text/plain' in content_type:
                # JSON / Texte brut
                categorie = 'json' if 'json' in content_type else 'text'
                try:
                    if 'application/json' in content_type:
                        json_data = response.json()
                        contenu = json.dumps(json_data, ensure_ascii=False)
                    else:
                        contenu = response.text
                except Exception:
                    contenu = response.text
                
            elif 'application/pdf' in content_type:
                # PDF
                categorie = 'pdf'
                contenu = self.extract_pdf_text(response.content)
                titre = self.extract_pdf_title(response.content) or titre
                
            elif content_type.startswith('image/'):
                # Image
                categorie = 'image'
                filename = self.download_file(url, response.content, content_type)
                metadata = self.extract_image_metadata(response.content)
                metadata['filename'] = filename
                ocr_text = metadata.get('ocr_text', '')
                contenu = f"Image: {metadata.get('alt', '')} {metadata.get('title', '')} {ocr_text}".strip()
                
            elif content_type.startswith('video/'):
                # Video
                categorie = 'video'
                filename = self.download_file(url, response.content, content_type)
                metadata = self.extract_video_metadata(response.content, filename)
                metadata['filename'] = filename
                contenu = f"Video: {metadata.get('duration', 0):.1f}s {metadata.get('width', 0)}x{metadata.get('height', 0)}"
                
            elif 'youtube.com' in url or 'youtu.be' in url:
                # YouTube
                categorie = 'video'
                metadata = self.extract_youtube_info(url)
                titre = metadata.get('title', titre)
                contenu = metadata.get('description', '')
                
            return {
                'url': response.url,
                'titre': titre,
                'contenu': contenu,
                'links': list(set(links)),
                'status': response.status_code,
                'success': True,
                'categorie': categorie,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Erreur crawling {url}: {e}")
            return {
                'url': url,
                'status': 0,
                'success': False,
                'erreur': str(e)
            }

    def extract_seo_metadata(self, soup: BeautifulSoup) -> dict:
        """Extrait les métadonnées SEO d'une page HTML"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name', '').lower()
            property = tag.get('property', '').lower()
            content = tag.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif property == 'og:title':
                metadata['og_title'] = content
            elif property == 'og:description':
                metadata['og_description'] = content
            elif property == 'og:image':
                metadata['og_image'] = content
        
        # H1 tags
        h1_tags = soup.find_all('h1')
        if h1_tags:
            metadata['h1'] = [h1.text.strip() for h1 in h1_tags]
        
        return metadata

    def analyze_media(self, soup: BeautifulSoup, base_url: str) -> dict:
        """Analyse les images et vidéos sur la page"""
        media_text = []
        media_urls = []
        
        # Images
        images = soup.find_all('img')
        for img in images:
            alt = img.get('alt', '')
            title = img.get('title', '')
            src = img.get('src', '')
            if src:
                absolute_src = urljoin(base_url, src)
                media_text.append(f"Image: {alt} {title} {absolute_src}")
                media_urls.append(absolute_src)
        
        # Videos
        videos = soup.find_all('video')
        for video in videos:
            src = video.get('src', '')
            if src:
                absolute_src = urljoin(base_url, src)
                media_text.append(f"Video: {absolute_src}")
                media_urls.append(absolute_src)
        
        # Vérifier si les images sont des data URLs (base64)
        data_images = [img for img in images if img.get('src', '').startswith('data:')]
        data_videos = [video for video in videos if video.get('src', '') and video.get('src', '').startswith('data:')]
        
        return {
            'media': ' '.join(media_text),
            'media_urls': media_urls,
            'image_count': len(images),
            'video_count': len(videos)
        }

    def extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extrait le texte d'un PDF"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text[:5000]  # Limiter la taille
        except Exception as e:
            logger.error(f"Erreur extraction PDF: {e}")
            return ""

    def extract_pdf_title(self, pdf_content: bytes) -> str:
        """Extrait le titre d'un PDF depuis les métadonnées"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            metadata = doc.metadata
            doc.close()
            return metadata.get('title', '')
        except Exception as e:
            logger.error(f"Erreur extraction titre PDF: {e}")
            return ""

    def download_file(self, url: str, content: bytes, content_type: str) -> str:
        """Télécharge un fichier média dans le dossier downloads"""
        try:
            # Générer un nom de fichier unique
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = mimetypes.guess_extension(content_type) or '.bin'
            filename = f"{url_hash}{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            return filename
        except Exception as e:
            logger.error(f"Erreur téléchargement {url}: {e}")
            return ""

    def extract_image_metadata(self, image_content: bytes) -> dict:
        """Extrait les métadonnées d'une image avec OCR"""
        try:
            img = Image.open(io.BytesIO(image_content))
            metadata = {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode
            }
            
            # Exif data
            if hasattr(img, '_getexif') and img._getexif():
                exif = img._getexif()
                if 274 in exif:  # Orientation
                    metadata['orientation'] = exif[274]
            
            # OCR - extraire le texte de l'image
            if HAS_TESSERACT:
                try:
                    # Convertir en RGB si nécessaire pour OCR
                    if img.mode not in ('L', 'RGB'):
                        img_ocr = img.convert('RGB')
                    else:
                        img_ocr = img
                    
                    # Extraire le texte avec pytesseract
                    ocr_text = pytesseract.image_to_string(img_ocr, lang='fra+eng')
                    if ocr_text.strip():
                        metadata['ocr_text'] = ocr_text.strip()
                        metadata['has_text'] = True
                    else:
                        metadata['has_text'] = False
                except ImportError:
                    # pytesseract n'est pas installé
                    metadata['has_text'] = False
                    logger.warning("pytesseract non installé - OCR désactivé")
                except Exception as ocr_error:
                    logger.warning(f"Erreur OCR: {ocr_error}")
                    metadata['has_text'] = False
            else:
                metadata['has_text'] = False
                logger.info("OCR non disponible - installer pytesseract pour l'extraction de texte d'images")
            
            img.close()
            return metadata
        except Exception as e:
            logger.error(f"Erreur extraction metadata image: {e}")
            return {}

    def extract_youtube_info(self, url: str) -> dict:
        """Extrait les informations d'une vidéo YouTube"""
        try:
            # Pour une vraie implémentation, utiliser l'API YouTube
            # Ici on simule avec une extraction basique
            video_id = None
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            
            if video_id:
                # Simulation des métadonnées
                return {
                    'video_id': video_id,
                    'title': f"YouTube Video {video_id}",
                    'description': f"Contenu YouTube: {url}",
                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                }
            return {}
        except Exception as e:
            logger.error(f"Erreur extraction YouTube: {e}")
            return {}

    def extract_video_metadata(self, video_content: bytes, filename: str) -> dict:
        """Extrait les métadonnées d'une vidéo"""
        try:
            # Sauvegarder temporairement le fichier vidéo
            temp_path = os.path.join(self.download_dir, f"temp_{filename}")
            with open(temp_path, 'wb') as f:
                f.write(video_content)
            
            metadata = {}
            
            # Utiliser OpenCV pour extraire les métadonnées
            if HAS_OPENCV:
                try:
                    cap = cv2.VideoCapture(temp_path)
                    if cap.isOpened():
                        metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        metadata['fps'] = cap.get(cv2.CAP_PROP_FPS)
                        metadata['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        duration = metadata['frame_count'] / metadata['fps'] if metadata['fps'] > 0 else 0
                        metadata['duration'] = duration
                        
                        # Extraire une miniature (première frame)
                        ret, frame = cap.read()
                        if ret:
                            thumbnail_path = os.path.join(self.download_dir, f"thumb_{filename}.jpg")
                            cv2.imwrite(thumbnail_path, frame)
                            metadata['thumbnail'] = f"thumb_{filename}.jpg"
                        
                        cap.release()
                except Exception as cv_error:
                    logger.warning(f"Erreur OpenCV: {cv_error}")
            else:
                logger.info("OpenCV non disponible - métadonnées vidéo limitées")
            
            # Utiliser moviepy pour des métadonnées supplémentaires
            if HAS_MOVIEPY:
                try:
                    clip = VideoFileClip(temp_path)
                    metadata['duration_clip'] = clip.duration
                    metadata['audio'] = clip.audio is not None
                    clip.close()
                except Exception as mp_error:
                    logger.warning(f"Erreur MoviePy: {mp_error}")
            else:
                logger.info("MoviePy non disponible - métadonnées vidéo limitées")
            
            # Supprimer le fichier temporaire
            try:
                os.remove(temp_path)
            except:
                pass
            
            return metadata
        except Exception as e:
            logger.error(f"Erreur extraction metadata vidéo: {e}")
            return {}
    
    def crawl(self, seed_urls: List[str]) -> List[dict]:
        """Lance le crawl récursif
        
        Args:
            seed_urls: URLs de départ
        
        Returns:
            Liste des pages crawlées
        """
        # Normaliser les URLs de départ
        self.to_visit = [self.normalize_url(u) for u in seed_urls]
        pages = []
        
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.normalize_url(self.to_visit.pop(0))
            
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
                    normalized_link = self.normalize_url(link)
                    if normalized_link in self.visited_urls:
                        continue
                    if self.is_valid_url(normalized_link, base_domain):
                        self.to_visit.append(normalized_link)
            else:
                logger.warning(f"Erreur crawling {url}: {result.get('erreur')}")
            
            # Respecter la politesse - délai entre requêtes
            if self.to_visit:  # Pas de délai après la dernière requête
                time.sleep(self.delay)
        
        logger.info(f"Crawl terminé: {len(pages)} pages téléchargées")
        return pages
