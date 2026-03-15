# 🚀 Guide de Lancement - SearchMine

Ce guide explique étape par étape comment lancer le projet SearchMine sur votre machine.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.8+** (recommandé : Python 3.11 ou supérieur)
- **XAMPP** (avec Apache et MySQL activés)
- **pip** (gestionnaire de paquets Python)

## ⚡ Étapes de lancement

### 1. Préparer l'environnement Python

Le projet utilise un environnement virtuel Python. Si ce n'est pas déjà fait :

```bash
# Aller dans le dossier du projet
cd c:\xampp\htdocs\Moteur_recherche

# Créer et activer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Sur Windows
```

### 2. Installer les dépendances

```bash
# Dans le dossier backend
cd backend

# Installer les paquets requis
pip install -r requirements.txt
```

**Dépendances principales :**
- Flask 3.0.3 (serveur web)
- Flask-CORS (gestion des requêtes cross-origin)
- mysql-connector-python (connexion MySQL)
- requests & beautifulsoup4 (crawler web)
- python-dotenv (variables d'environnement)

### 3. Configurer la base de données

#### Option A : Via phpMyAdmin (recommandé pour débutants)

1. Démarrer XAMPP (Apache + MySQL)
2. Ouvrir http://localhost/phpmyadmin
3. Créer une base de données nommée `moteur_recherche`
4. Sélectionner la base → Onglet "Importer"
5. Choisir le fichier `database/schema_v2.sql`
6. Cliquer "Exécuter"

#### Option B : Via ligne de commande

```bash
# Assurer que MySQL est démarré dans XAMPP
mysql -u root < database\schema_v2.sql
```

### 4. Peupler la base de données

```bash
# Depuis le dossier backend
python populate_database.py
```

Cette commande ajoute 66 documents d'exemple pour tester le moteur de recherche.

### 5. Lancer le serveur

```bash
# Depuis le dossier backend
python app_v2.py
```

Vous devriez voir :
```
* Running on http://127.0.0.1:5000
* Running on http://localhost:5000
```

Le serveur tourne maintenant sur le port 5000.

### 6. Accéder à l'application

Ouvrez votre navigateur et allez à :
- **Interface de recherche** : http://localhost:5000/
- **Interface d'administration** : http://localhost:5000/admin

## 🔧 Configuration avancée

### Variables d'environnement

Créer un fichier `.env` dans le dossier `backend/` pour personnaliser :

```env
# Configuration MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=moteur_recherche

# Configuration Flask
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Démarrage automatique

Pour lancer automatiquement au démarrage :
- Créer un script batch `start_server.bat` :
```batch
@echo off
cd /d c:\xampp\htdocs\Moteur_recherche\backend
call ..\..\.venv\Scripts\activate
python app_v2.py
```

## 🐛 Dépannage

### Erreur "Module not found"
- Vérifier que l'environnement virtuel est activé
- Réinstaller : `pip install -r requirements.txt`

### Erreur MySQL
- Vérifier que MySQL est démarré dans XAMPP
- Vérifier les identifiants dans `config.py`

### Port 5000 occupé
- Changer le port dans `config.py` ou tuer le processus :
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problème de codage
- Assurer que les fichiers sont en UTF-8
- Base de données en `utf8mb4_unicode_ci`

## 🎯 Test du projet

Une fois lancé, testez avec ces recherches :
- "Python"
- "Web development"
- "Machine Learning"
- "Flask tutorial"

## 📁 Structure du projet

```
Moteur_recherche/
├── backend/           # Code Python (Flask)
│   ├── app_v2.py     # Serveur principal
│   ├── config.py     # Configuration
│   ├── services.py   # Services métier
│   └── ...
├── database/         # Schéma SQL
├── frontend/         # Interface web (HTML/CSS/JS)
└── .venv/           # Environnement virtuel Python
```

## ❓ Support

Si vous rencontrez des problèmes :
1. Vérifier les logs du serveur Flask
2. Tester l'endpoint health : http://localhost:5000/api/health
3. Vérifier la connexion MySQL avec phpMyAdmin

Le projet est maintenant prêt à fonctionner ! 🎉</content>
<parameter name="filePath">c:\xampp\htdocs\Moteur_recherche\GUIDE_LANCEMENT.md