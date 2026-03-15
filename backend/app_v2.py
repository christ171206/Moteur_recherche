from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import DEBUG, HOST, PORT
from services import DatabaseService, SearchService
from crawler import WebCrawler
from indexer import Indexer
from ranking import BM25Ranker
from google_features import GoogleLikeFeatures
import logging
from datetime import datetime
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# ===================================================
# FRONTEND ROUTES
# ===================================================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'google.html')

@app.route('/admin')
def admin():
    return send_from_directory(app.static_folder, 'admin.html')

# ===================================================
# ERROR HANDLERS
# ===================================================
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Requête invalide', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ressource non trouvée'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Erreur serveur: {error}")
    return jsonify({'error': 'Erreur serveur interne'}), 500

# ===================================================
# MEDIA FILES SERVING
# ===================================================
@app.route('/media/<path:filename>')
def serve_media(filename):
    """Sert les fichiers médias téléchargés (images, vidéos, etc.)"""
    try:
        media_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        return send_from_directory(media_dir, filename)
    except Exception as e:
        logger.error(f"Erreur service média {filename}: {e}")
        return jsonify({'error': 'Fichier média non trouvé'}), 404

# ===================================================
# HEALTH CHECK
# ===================================================
@app.route('/api/health', methods=['GET'])
def health():
    """Vérifie la santé du serveur"""
    try:
        conn = DatabaseService.get_connection()
        conn.close()
        return jsonify({
            'status': 'OK',
            'message': 'Serveur et BD fonctionnent correctement',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return jsonify({
            'status': 'ERROR',
            'message': str(e)
        }), 500

# ===================================================
# SEARCH ENDPOINTS
# ===================================================
@app.route('/api/search', methods=['GET'])
def search():
    """Endpoint de recherche
    
    Parameters:
    - q: requête (requis)
    - categorie: filtre par catégorie (optionnel)
    - tags: filtre par tags (optionnel)
    - date_from: date minimale (optionnel)
    - date_to: date maximale (optionnel)
    - limit: nombre de résultats (optionnel, default=20)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'error': "Paramètre 'q' manquant"}), 400
        
        # Récupérer les filtres
        filters = {}
        if request.args.get('categorie'):
            filters['categorie'] = request.args.get('categorie')
        if request.args.get('tags'):
            filters['tags'] = request.args.get('tags')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        if request.args.get('auteur'):
            filters['auteur'] = request.args.get('auteur')
        
        # Effectuer la recherche
        result = SearchService.search(query, filters, limit)
        
        return jsonify(result.to_dict()), 200
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """Autocomplétion
    
    Parameters:
    - q: requête partielle
    """
    try:
        partial = request.args.get('q', '').strip()
        
        if len(partial) < 2:
            return jsonify({'suggestions': []}), 200
        
        suggestions = SearchService.get_suggestions(partial)
        
        return jsonify({'suggestions': suggestions}), 200
    except Exception as e:
        logger.error(f"Erreur autocomplete: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Récupère les statistiques globales et tendances"""
    try:
        stats = SearchService.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Erreur statistiques: {e}")
        return jsonify({'error': str(e)}), 500

# ===================================================
# IMAGE/VIDEO SEARCH ENDPOINTS
# ===================================================
@app.route('/api/search/images', methods=['GET'])
def search_images():
    """Recherche d'images
    
    Parameters:
    - q: requête (optionnel pour recherche générale d'images)
    - limit: nombre de résultats (optionnel, default=20)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        # Recherche dans la catégorie 'image'
        filters = {'categorie': 'image'}
        result = SearchService.search(query, filters, limit)
        
        return jsonify(result.to_dict()), 200
    except Exception as e:
        logger.error(f"Erreur recherche images: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/videos', methods=['GET'])
def search_videos():
    """Recherche de vidéos
    
    Parameters:
    - q: requête (optionnel pour recherche générale de vidéos)
    - limit: nombre de résultats (optionnel, default=20)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        # Recherche dans la catégorie 'video'
        filters = {'categorie': 'video'}
        result = SearchService.search(query, filters, limit)
        
        return jsonify(result.to_dict()), 200
    except Exception as e:
        logger.error(f"Erreur recherche vidéos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/reverse-image', methods=['POST'])
def reverse_image_search():
    """Recherche par image inversée (upload d'image)
    
    Body: Form-data avec fichier 'image'
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucun fichier image fourni'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        # Lire le contenu de l'image
        image_content = image_file.read()
        
        # Extraire le texte OCR de l'image uploadée
        from crawler import WebCrawler
        crawler = WebCrawler()
        ocr_metadata = crawler.extract_image_metadata(image_content)
        ocr_text = ocr_metadata.get('ocr_text', '')
        
        if not ocr_text:
            return jsonify({
                'message': 'Aucun texte détecté dans l\'image',
                'results': []
            }), 200
        
        # Rechercher avec le texte OCR
        filters = {'categorie': 'image'}
        result = SearchService.search(ocr_text, filters, 20)
        
        return jsonify({
            'ocr_text': ocr_text,
            'results': result.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Erreur recherche image inversée: {e}")
        return jsonify({'error': str(e)}), 500

# ===================================================
# DOCUMENT ENDPOINTS
# ===================================================
@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Récupère tous les documents"""
    try:
        documents = DatabaseService.get_all_documents()
        return jsonify({
            'nb_documents': len(documents),
            'documents': [doc.to_dict() for doc in documents]
        }), 200
    except Exception as e:
        logger.error(f"Erreur récupération documents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['POST'])
def create_document():
    """Crée un nouveau document
    
    Body payload:
    {
        "titre": "...",
        "description": "...",
        "contenu": "...",
        "categorie": "...",
        "tags": "tag1,tag2,tag3",
        "auteur": "...",
        "url": "...",
        "date_publication": "YYYY-MM-DD"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('titre') or not data.get('contenu'):
            return jsonify({'error': 'Titre et contenu requis'}), 400
        
        doc_id = DatabaseService.add_document(
            titre=data.get('titre'),
            description=data.get('description', ''),
            contenu=data.get('contenu'),
            categorie=data.get('categorie', 'General'),
            tags=data.get('tags', ''),
            auteur=data.get('auteur', 'Anonyme'),
            url=data.get('url'),
            date_publication=data.get('date_publication')
        )
        
        logger.info(f"Document créé: ID={doc_id}")
        return jsonify({
            'id': doc_id,
            'message': 'Document ajouté avec succès'
        }), 201
    except Exception as e:
        logger.error(f"Erreur création document: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id: int):
    """Récupère un document par ID"""
    try:
        document = DatabaseService.get_document_by_id(doc_id)
        
        if not document:
            return jsonify({'error': 'Document non trouvé'}), 404
        
        # Enregistrer la vue
        DatabaseService.increment_views(doc_id)
        
        return jsonify(document.to_dict()), 200
    except Exception as e:
        logger.error(f"Erreur récupération document: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id: int):
    """Supprime un document"""
    try:
        success = DatabaseService.delete_document(doc_id)
        
        if not success:
            return jsonify({'error': 'Document non trouvé'}), 404
        
        return jsonify({'message': 'Document supprimé avec succès'}), 200
    except Exception as e:
        logger.error(f"Erreur suppression document: {e}")
        return jsonify({'error': str(e)}), 500

# ===================================================
# CRAWLER & INDEXER ENDPOINTS
# ===================================================
@app.route('/api/crawler/start', methods=['POST'])
def start_crawler():
    """Lance le crawl d'URLs
    
    Body payload:
    {
        "urls": ["http://example.com", "https://site.com"],
        "max_pages": 50,
        "delay": 1.0
    }
    """
    try:
        data = request.get_json()
        
        urls = data.get('urls', [])
        max_pages = data.get('max_pages', 50)
        delay = data.get('delay', 1.0)
        
        if not urls:
            return jsonify({'error': 'Paramètre "urls" requis'}), 400
        
        if not isinstance(urls, list):
            return jsonify({'error': 'urls doit être une liste'}), 400
        
        logger.info(f"Début du crawl: {len(urls)} URLs, {max_pages} pages max")
        
        # Initialiser le crawler
        crawler = WebCrawler(max_pages=max_pages, delay=delay)
        
        # Crawler les pages
        pages = crawler.crawl(urls)
        
        # Indexer les pages
        indexing_result = Indexer.index_pages(pages)
        
        return jsonify({
            'message': 'Crawl et indexation terminés',
            'pages_crawlees': len(pages),
            'pages_indexees': indexing_result['reussis'],
            'erreurs': indexing_result['echoues'],
            'details': indexing_result['details'][:10]  # Limiter les détails
        }), 200
    except Exception as e:
        logger.error(f"Erreur crawl: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawler/status', methods=['GET'])
def crawler_status():
    """Statut du crawler"""
    return jsonify({
        'status': 'OK',
        'crawler_available': True,
        'max_pages_default': 50,
        'delay_default': 1.0,
        'message': 'Envoyer une requête POST à /api/crawler/start pour lancer un crawl'
    })

@app.route('/api/indexer/status', methods=['GET'])
def indexer_status():
    """Statut de l'indexer"""
    try:
        total_docs = len(DatabaseService.get_all_documents())
        return jsonify({
            'status': 'OK',
            'documents_indexes': total_docs,
            'indexer_available': True
        })
    except Exception as e:
        logger.error(f"Erreur statut indexer: {e}")
        return jsonify({'error': str(e)}), 500

# ===================================================
# GOOGLE-LIKE FEATURES ENDPOINTS
# ===================================================
@app.route('/api/features/featured-snippet', methods=['POST'])
def featured_snippet():
    """Extrait une featured snippet pour une requête
    
    Body payload:
    {
        "query": "...",
        "documents": [...] ou 
        "document_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Paramètre query requis'}), 400
        
        # Récupérer les documents
        documents = []
        
        if 'documents' in data:
            # Documents fournis directement (du résultat de recherche)
            documents = data.get('documents', [])
        elif 'document_ids' in data:
            # IDs fournis, récupérer les documents
            doc_ids = data.get('document_ids', [])
            documents = [
                DatabaseService.get_document_by_id(doc_id).to_dict()
                for doc_id in doc_ids
                if DatabaseService.get_document_by_id(doc_id)
            ]
        
        if not documents:
            return jsonify({'snippet': None}), 200
        
        # Extraire la featured snippet
        snippet_text = GoogleLikeFeatures.extract_featured_snippet(
            ' '.join([d.get('contenu', '') if isinstance(d, dict) else d.contenu for d in documents]),
            query
        )
        
        if snippet_text:
            return jsonify({
                'snippet': {
                    'text': snippet_text,
                    'title': query,
                    'source_url': documents[0].get('url') if isinstance(documents[0], dict) else documents[0].url
                }
            }), 200
        else:
            return jsonify({'snippet': None}), 200
            
    except Exception as e:
        logger.error(f"Erreur featured snippet: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/suggestions', methods=['POST'])
def suggestions():
    """Retourne les suggestions "did you mean"
    
    Body payload:
    {
        "query": "..."
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'suggestions': []}), 200
        
        # Récupérer tous les documents pour extraire les suggestions
        all_docs = DatabaseService.get_all_documents()
        
        suggestions = GoogleLikeFeatures.get_suggestions(query, all_docs)
        
        return jsonify({'suggestions': suggestions}), 200
    except Exception as e:
        logger.error(f"Erreur suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/answers', methods=['POST'])
def answers():
    """Extrait les réponses directes pour une requête
    
    Body payload:
    {
        "query": "...",
        "document_ids": [1, 2, 3] ou
        "documents": [...]
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Paramètre query requis'}), 400
        
        # Récupérer les documents
        documents = []
        
        if 'documents' in data:
            documents = data.get('documents', [])
        elif 'document_ids' in data:
            doc_ids = data.get('document_ids', [])
            documents = [
                DatabaseService.get_document_by_id(doc_id)
                for doc_id in doc_ids
                if DatabaseService.get_document_by_id(doc_id)
            ]
        
        if not documents:
            return jsonify({'answers': []}), 200
        
        # Extraire les réponses
        answers_list = []
        for doc in documents:
            content = doc.get('contenu') if isinstance(doc, dict) else doc.contenu
            answer = GoogleLikeFeatures.extract_answer(content, query)
            if answer:
                answers_list.append({
                    'answer': answer,
                    'source': doc.get('titre') if isinstance(doc, dict) else doc.titre,
                    'url': doc.get('url') if isinstance(doc, dict) else doc.url
                })
        
        return jsonify({'answers': answers_list[:3]}), 200  # Limiter à 3 réponses
    except Exception as e:
        logger.error(f"Erreur answers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/query-expansion', methods=['POST'])
def query_expansion():
    """Expansion de requête avec synonymes et termes connexes
    
    Body payload:
    {
        "query": "..."
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Paramètre query requis'}), 400
        
        expanded = GoogleLikeFeatures.expand_query(query)
        
        return jsonify({
            'original_query': query,
            'expanded_terms': expanded,
            'num_expanded': len(expanded)
        }), 200
    except Exception as e:
        logger.error(f"Erreur query expansion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/bm25', methods=['POST'])
def search_bm25():
    """Recherche avec BM25 ranking
    
    Body payload:
    {
        "query": "...",
        "limit": 20,
        "offset": 0,
        "filters": {...}
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)
        offset = data.get('offset', 0)
        
        if not query:
            return jsonify({'error': "Paramètre 'query' manquant"}), 400
        
        # Recherche classique d'abord
        result = SearchService.search(query, data.get('filters', {}), limit + offset)
        
        results = result.results
        
        if results:
            # Appliquer BM25 ranking
            ranker = BM25Ranker([r.content for r in results])
            ranked_results = ranker.rank(query, results)
            
            # Paginer
            ranked_results = ranked_results[offset:offset+limit]
            
            return jsonify({
                'query': query,
                'total_results': result.total_results,
                'results': [r.to_dict() if hasattr(r, 'to_dict') else r for r in ranked_results],
                'search_time': result.search_time,
                'ranking_algorithm': 'BM25'
            }), 200
        else:
            return jsonify({
                'query': query,
                'total_results': 0,
                'results': [],
                'search_time': result.search_time,
                'ranking_algorithm': 'BM25'
            }), 200
            
    except Exception as e:
        logger.error(f"Erreur BM25 search: {e}")
        return jsonify({'error': str(e)}), 500

# ===================================================
# START SERVER
# ===================================================
if __name__ == '__main__':
    logger.info(f"Démarrage du serveur sur {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
