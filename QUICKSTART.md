# 🚀 SearchMine - Guide de Démarrage Rapide

Un moteur de recherche professionnel de type Google avec crawling, indexation et ranking avancé (BM25).

---

## 📋 Prérequis

- **Xampp** avec Apache et MySQL démarrés
- **Python 3.8+** installé
- **pip** pour gérer les dépendances Python

---

## ⚡ Démarrage en 5 minutes

### **1. Initialiser la Base de Données**

```bash
# Ouvrir phpMyAdmin
# http://localhost/phpmyadmin

# Créer une nouvelle base de données
# Nom: moteur_recherche
# Charset: utf8mb4_unicode_ci

# Importer le schéma
# Aller à: Importer
# Sélectionner: database/schema_v2.sql
# Cliquer "Exécuter"
```

Ou en ligne de commande MySQL:
```bash
mysql -u root < database\schema_v2.sql
```

### **2. Installer les Dépendances Python**

```bash
cd backend
pip install -r requirements.txt
```

**Dépendances:**
- Flask (API web)
- Flask-CORS (Cross-origin requests)
- mysql-connector-python (Connexion MySQL)
- requests (Web crawler HTTP)
- beautifulsoup4 (Parsing HTML)

### **3. Lancer le Backend**

```bash
cd backend
python app_v2.py
```

✅ Le serveur démarre sur `http://localhost:5000`

Vérifier la santé:
```bash
curl http://localhost:5000/api/health
```

### **4. Ouvrir le Frontend**

La structure du projet sur Xampp:
```
C:\Xampp\htdocs\Moteur-recherche\
├── backend/           # API Flask
├── frontend/          # Interface utilisateur
│   ├── google.html    # Moteur de recherche (comme Google)
│   ├── admin.html     # Interface d'administration
│   └── google_style.css, script_google.js
└── database/          # Schéma MySQL
```

**Ouvrir dans le navigateur:**
- **Recherche:** http://localhost/Moteur-recherche/frontend/google.html
- **Admin (Crawler):** http://localhost/Moteur-recherche/frontend/admin.html

---

## 🎯 Utilisation

### **Chercher (google.html)**
1. Accéder à `frontend/google.html`
2. Taper une requête
3. Voir les résultats classés par BM25
4. Featured snippets affichés automatiquement

### **Recherche d'Images**
1. Cliquer sur l'icône d'appareil photo dans la barre de recherche
2. Sélectionner une image depuis votre ordinateur
3. Le système extrait automatiquement le texte de l'image (OCR)
4. Recherche d'images similaires basée sur le contenu textuel

### **Recherche de Vidéos**
1. Cliquer sur l'onglet "Videos" dans les résultats de recherche
2. Taper une requête pour rechercher des vidéos
3. Voir les vidéos crawlées avec métadonnées (durée, résolution, etc.)

### **Affichage Visuel des Résultats**
- **Recherches générales** : Incluent automatiquement des images et vidéos pertinentes
- **Mode Grille** : Pour les recherches d'images/vidéos, affichage en grille avec miniatures
- **Mode Liste** : Pour les recherches textuelles traditionnelles
- **Médias Locaux** : Les fichiers téléchargés s'affichent directement depuis le serveur

### **Crawler et Indexer (admin.html)**
1. Accéder à `frontend/admin.html`
2. Onglet **Crawler**:
   - Entrer une URL (ex: `https://wikipedia.org`)
   - Configurer max pages (20-50)
   - Délai entre requêtes (1-2 secondes)
   - Cliquer "Démarrer le crawl"
3. Les pages sont crawlées et indexées automatiquement
4. Voir dans l'onglet **Documents** toutes les pages indexées

---

## 📂 Structure du Projet

```
Moteur-recherche/
│
├── backend/
│   ├── app_v2.py              # Flask API principale
│   ├── config.py              # Configuration (MySQL, port, etc.)
│   ├── models.py              # Modèles de données
│   ├── services.py            # Couche métier (recherche, BD)
│   ├── crawler.py             # Web crawler (BeautifulSoup)
│   ├── indexer.py             # Indexeur (insertion en BD)
│   ├── ranking.py             # Algorithme BM25
│   ├── google_features.py     # Features Google (snippets, suggestions)
│   └── requirements.txt        # Dépendances
│
├── frontend/
│   ├── google.html            # Interface de recherche (comme Google)
│   ├── google_style.css       # Stylisation Google
│   ├── script_google.js       # JavaScript (API calls)
│   └── admin.html             # Interface d'administration
│
├── database/
│   └── schema_v2.sql          # Schéma MySQL complet
│
├── CAHIER DES CHARGES 2026.pdf    # Spécification du projet
└── QUICKSTART.md              # Ce fichier
```

---

## 🔧 API REST

### **Recherche d'Images**
```bash
GET /api/search/images?q=chat&limit=20
```

### **Recherche de Vidéos**
```bash
GET /api/search/videos?q=tutoriel&limit=20
```

### **Recherche par Image Inversée**
```bash
POST /api/search/reverse-image
Content-Type: multipart/form-data

# Avec fichier image dans le body
```

Réponse pour recherche image inversée:
```json
{
  "ocr_text": "Texte extrait de l'image",
  "results": {
    "results": [...],
    "total_results": 15,
    "search_time": 0.045
  }
}
```

### **Recherche**
```bash
POST /api/search
{
  "query": "python",
  "limit": 10,
  "offset": 0
}
```

Réponse:
```json
{
  "results": [
    {
      "id": 1,
      "titre": "...",
      "url": "...",
      "snippet": "...",
      "relevance_score": 0.87
    }
  ],
  "total_results": 150,
  "search_time": 0.023
}
```

### **Crawler (Admin)**
```bash
POST /api/crawler/start
{
  "urls": ["https://example.com"],
  "max_pages": 20,
  "delay": 1.0
}
```

### **Documents**
```bash
GET /api/documents              # Tous les documents
GET /api/documents/1            # Document par ID
DELETE /api/documents/1         # Supprimer
POST /api/documents             # Créer nouveau
```

### **Features Google**
```bash
POST /api/features/featured-snippet    # Snippet principal
POST /api/features/suggestions         # "Did you mean"
POST /api/features/answers             # Réponses directes
POST /api/search/bm25                  # Recherche BM25
```

### **Statut**
```bash
GET /api/health                 # Vérifier la connexion
GET /api/statistics             # Stats globales
```

---

## 📊 Algorithmes & Features

### **Ranking**
- **BM25**: Algorithme professionnel de ranking (meilleur que TF-IDF)
- Avec paramètres tuning: k1=2.0, b=0.75
- Field-weighted scores (titre boost)

### **Google-like Features**
- ✅ Featured snippets (extraits directs)
- ✅ Did-you-mean suggestions
- ✅ Direct answers extraction
- ✅ Query expansion avec synonymes
- ✅ **Recherche d'images avec OCR**
- ✅ **Recherche de vidéos avec métadonnées**
- ✅ **Recherche par image inversée**

### **Web Crawler**
- Crawl récursif avec déduplication d'URLs
- Extraction métadonnées (titre, description, date)
- **Traitement d'images avec OCR (extraction de texte)**
- **Extraction de métadonnées vidéos (durée, résolution, miniatures)**
- Téléchargement automatique des médias
- Respect des délais (politesse)
- Gestion erreurs et timeouts
- User-Agent professionnel

### **Indexation**
- Stockage en MySQL avec FULLTEXT indexes
- Catégorisation automatique par domaine
- Statstics & analytics tracking
- Support tags et filtres

---

## 🐛 Dépannage

### **Erreur de connexion MySQL**
```
Error: Connection to MySQL failed
```
**Solution:**
1. Vérifier que MySQL/Xampp est démarré
2. Vérifier `backend/config.py` (host=localhost, user=root, password='')
3. Vérifier que la BD `moteur_recherche` existe

### **Erreur 404 Frontend**
```
Cannot find google.html
```
**Solution:**
- S'assurer que les fichiers frontend sont dans:
  `C:\Xampp\htdocs\Moteur-recherche\frontend\`

### **Erreur CORS Frontend → Backend**
```
CORS error accessing localhost:5000
```
**Solution:**
- Flask-CORS est activé dans `app_v2.py`
- Vérifier que le backend demarre sur le bon port (par défaut 5000)

### **Crawler très lent**
- Augmenter le `delay` dans admin.html (1.0 par défaut)
- Réduire `max_pages`
- Vérifier la connexion réseau

---

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| `backend/app_v2.py` | API Flask avec tous les endpoints |
| `backend/services.py` | Logic recherche & BD |
| `backend/crawler.py` | Web crawler récursif |
| `backend/ranking.py` | BM25 ranking algorithm |
| `frontend/google_style.css` | Design Google |
| `database/schema_v2.sql` | Tables MySQL (documents, stats, indexes) |

---

## 🎓 Caractéristiques du Projet (L3)

✅ **API REST** complète en Flask  
✅ **Web Crawler** avec BeautifulSoup4  
✅ **Indexation** full-text en MySQL  
✅ **Ranking** professionnel (BM25)  
✅ **Features Google** (snippets, suggestions)  
✅ **Recherche d'Images** avec OCR intégré  
✅ **Recherche de Vidéos** avec métadonnées  
✅ **Recherche par Image Inversée**  
✅ **Affichage Visuel** en grille pour les médias  
✅ **Médias Locaux** servis directement  
✅ **Frontend** moderne (responsive, Google-style)  
✅ **Admin Interface** pour gérer crawl/documents  
✅ **Architecture** 3-layer (Models → Services → API)  

---

## 🚀 Prochaines Étapes

1. **Tester la recherche**: Entrer des requêtes dans `google.html`
2. **Crawler un site**: Admin → Crawler → Ajouter URL → Lancer
3. **Vérifier les documents**: Admin → Documents → Voir tous
4. **Optimiser**: Ajuster BM25 parameters en `ranking.py`
5. **Déployer**: Configuration production en `config.py`

---

## 📞 Support

- **API Health Check**: `http://localhost:5000/api/health`
- **Admin Interface**: `http://localhost/Moteur-recherche/frontend/admin.html`
- **Database**: phpMyAdmin → `moteur_recherche`

Bon courage! 🎉
