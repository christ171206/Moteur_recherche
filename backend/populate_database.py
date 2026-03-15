#!/usr/bin/env python3
"""
Script de population massive de la base de données SearchMine
Insère 100+ documents pertinents pour avoir une bonne base de recherche
"""

import mysql.connector
from datetime import datetime, timedelta
import random

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'moteur_recherche'
}

# Documents à insérer
DOCUMENTS = [
    # === PYTHON (15 docs) ===
    {
        'titre': 'Introduction à Python',
        'description': 'Les bases du langage de programmation Python',
        'contenu': '''Python est un langage de programmation interprété créé par Guido van Rossum en 1991. 
        Il est très populaire pour l'apprentissage et le développement rapide d'applications. 
        Python supporte la programmation orientée objet, procédurale et fonctionnelle.
        Sa syntaxe simple et lisible le rend accessible aux débutants.''',
        'url': 'https://python.org/docs/introduction',
        'categorie': 'Programmation',
        'auteur': 'Python Foundation',
        'tags': 'python,langage,tutoriel'
    },
    {
        'titre': 'Python: Variables et Types de Données',
        'description': 'Comprendre les variables et types en Python',
        'contenu': '''En Python, les variables sont des conteneurs pour stocker des valeurs de données.
        Les principaux types sont: int (entiers), float (nombres décimaux), str (chaînes), bool (booléens).
        Python est un langage typé dynamiquement - vous n\'avez pas besoin de déclarer le type.''',
        'url': 'https://python.org/docs/variables',
        'categorie': 'Programmation',
        'auteur': 'Python Academy',
        'tags': 'python,variables,types,données'
    },
    {
        'titre': 'Fonctions et Modules Python',
        'description': 'Créer et utiliser des fonctions et modules',
        'contenu': '''Les fonctions sont des blocs de code réutilisables. Vous les définissez avec def.
        Les modules sont des fichiers Python contenant des fonctions, classes et variables.
        Python inclut de nombreux modules intégrés comme os, sys, math, random.''',
        'url': 'https://python.org/docs/functions',
        'categorie': 'Programmation',
        'auteur': 'Python Core',
        'tags': 'python,fonctions,modules'
    },
    {
        'titre': 'Programmation Orientée Objet en Python',
        'description': 'Classes, objets et héritage en Python',
        'contenu': '''La programmation orientée objet (POO) est un paradigme basé sur des objets.
        Une classe est un modèle pour créer des objets. L'héritage permet de créer des relations entre classes.
        L'encapsulation cache les données internes et expose les interfaces publiques.''',
        'url': 'https://python.org/docs/oop',
        'categorie': 'Programmation',
        'auteur': 'Advanced Python',
        'tags': 'python,oop,classes,héritage'
    },
    {
        'titre': 'Gestion des Exceptions en Python',
        'description': 'Try, except, finally pour gérer les erreurs',
        'contenu': '''Les exceptions sont des erreurs qui se produisent lors de l\'exécution.
        Utilisez try/except pour les capturer et les gérer. Finally exécute du code de nettoyage.
        Les exceptions personnalisées permettent une gestion d\'erreurs plus précise.''',
        'url': 'https://python.org/docs/exceptions',
        'categorie': 'Programmation',
        'auteur': 'Python Error Handling',
        'tags': 'python,exceptions,erreurs,try,except'
    },
    {
        'titre': 'Listes, Tuples et Dictionnaires',
        'description': 'Structures de données essentielles en Python',
        'contenu': '''Les listes sont des collections ordonnées et mutables [1, 2, 3].
        Les tuples sont immutables (1, 2, 3). Les dictionnaires stockent des paires clé-valeur.
        Chaque structure a des opérations particulières optimisées.''',
        'url': 'https://python.org/docs/datastructures',
        'categorie': 'Programmation',
        'auteur': 'Python Collections',
        'tags': 'python,listes,tuples,dictionnaires,structures'
    },
    {
        'titre': 'Compréhensions de Liste en Python',
        'description': 'Créer des listes de manière concise',
        'contenu': '''Les compréhensions permettent de créer des listes en une seule ligne.
        Syntaxe: [expression for item in iterable if condition]
        C\'est une alternative au code boucle plus concise et lisible.''',
        'url': 'https://python.org/docs/comprehensions',
        'categorie': 'Programmation',
        'auteur': 'Python Style',
        'tags': 'python,compréhension,listes,fonctionnel'
    },
    {
        'titre': 'Décorateurs Python',
        'description': 'Modifier le comportement des fonctions',
        'contenu': '''Les décorateurs sont des fonctions qui modifient d\'autres fonctions ou classes.
        Syntaxe: @decorator. Ils sont très utiles pour la validation, la mise en cache, et logging.
        Python inclut des décorateurs intégrés comme @property et @staticmethod.''',
        'url': 'https://python.org/docs/decorators',
        'categorie': 'Programmation',
        'auteur': 'Advanced Patterns',
        'tags': 'python,décorateurs,fonctions,patterns'
    },
    {
        'titre': 'Gestion des Fichiers en Python',
        'description': 'Lire et écrire des fichiers',
        'contenu': '''Utilisez open() pour accéder aux fichiers. Modes: r (lecture), w (écriture), a (ajout).
        Context managers (with) assurent la fermeture des fichiers automatiquement.
        Python supporte CSV, JSON, XML et d\'autres formats.''',
        'url': 'https://python.org/docs/files',
        'categorie': 'Programmation',
        'auteur': 'File Management',
        'tags': 'python,fichiers,io,csv,json'
    },
    {
        'titre': 'Expressions Régulières en Python',
        'description': 'Traiter le texte avec regex',
        'contenu': '''Le module re permet de chercher et remplacer du texte avec des patterns.
        Patterns: . (tout), * (0+), + (1+), ? (0-1), [] (ensemble), ^ (début), $ (fin).
        Fonctions principales: search(), findall(), sub(), split().''',
        'url': 'https://python.org/docs/regex',
        'categorie': 'Programmation',
        'auteur': 'Text Processing',
        'tags': 'python,regex,expressions régulières,texte'
    },
    {
        'titre': 'NumPy pour l\'Analyse Numérique',
        'description': 'Calculs scientifiques et matriciels',
        'contenu': '''NumPy est la librairie pour le calcul numérique en Python.
        Elle fournit des arrays n-dimensionnels et des opérations mathématiques.
        Parfait pour la physique, les statistiques et le machine learning.''',
        'url': 'https://numpy.org',
        'categorie': 'Data Science',
        'auteur': 'NumPy Community',
        'tags': 'python,numpy,calcul,science,data'
    },
    {
        'titre': 'Pandas pour la Manipulation de Données',
        'description': 'Analyser et transformer des données',
        'contenu': '''Pandas fournit des DataFrames pour manipuler des données comme Excel.
        Opérations: filtrer, trier, grouper, joindre, agréger.
        Idéal pour le nettoyage et la préparation de données.''',
        'url': 'https://pandas.pydata.org',
        'categorie': 'Data Science',
        'auteur': 'Pandas Team',
        'tags': 'python,pandas,data,analyse,dataframe'
    },
    {
        'titre': 'Visualisation avec Matplotlib',
        'description': 'Créer des graphiques et visualisations',
        'contenu': '''Matplotlib crée des graphiques statiques, animés et interactifs.
        Types: linéaire, barres, histogrammes, camemberts, scatter plots.
        Compatible avec NumPy et Pandas pour la visualisation de données.''',
        'url': 'https://matplotlib.org',
        'categorie': 'Data Science',
        'auteur': 'Matplotlib Developers',
        'tags': 'python,matplotlib,visualisation,graphiques'
    },
    {
        'titre': 'Asyncio et Programmation Asynchrone',
        'description': 'Programmation concurrente en Python',
        'contenu': '''Asyncio permettent aux programmes de faire plusieurs choses à la fois.
        async/await syntax pour les coroutines. Utile pour les requêtes réseau et I/O.
        Alternative à threading avec moins de surcharge.''',
        'url': 'https://python.org/docs/asyncio',
        'categorie': 'Programmation Avancée',
        'auteur': 'Python Core',
        'tags': 'python,async,concurrent,asyncio'
    },

    # === WEB & FRAMEWORKS (15 docs) ===
    {
        'titre': 'Introduction à Flask',
        'description': 'Framework web léger pour Python',
        'contenu': '''Flask est un micro-framework web Python. Il fournit les outils pour créer des sites web.
        Étapes: définir des routes, créer des templates, gérer les requêtes HTTP.
        Parfait pour commencer avec le développement web.''',
        'url': 'https://flask.palletsprojects.com',
        'categorie': 'Web',
        'auteur': 'Armin Ronacher',
        'tags': 'flask,python,web,framework'
    },
    {
        'titre': 'Routing et URLs en Flask',
        'description': 'Mapper les URLs aux fonctions',
        'contenu': '''Les routes associent les URLs à des fonctions Python.
        Décorateur @app.route(\'/path\'). Paramètres: /user/<name> capture le nom.
        Méthodes: GET, POST, PUT, DELETE selon l\'opération.''',
        'url': 'https://flask.palletsprojects.com/routing',
        'categorie': 'Web',
        'auteur': 'Flask Docs',
        'tags': 'flask,routing,urls,http'
    },
    {
        'titre': 'Requêtes et Réponses HTTP',
        'description': 'Comprendre HTTP en Flask',
        'contenu': '''HTTP est le protocole client-serveur du web.
        Requête: demande du client. Réponse: données du serveur.
        Status codes: 200 (OK), 404 (Not Found), 500 (Error).''',
        'url': 'https://flask.palletsprojects.com/requests',
        'categorie': 'Web',
        'auteur': 'Web Standards',
        'tags': 'http,web,requêtes,réponses'
    },
    {
        'titre': 'Templates Jinja2',
        'description': 'Créer des pages HTML dynamiques',
        'contenu': '''Jinja2 est un moteur de templates pour Flask.
        Syntaxe: {{ variable }}, {% if condition %}, {% for item in items %}.
        Permet de générer du HTML avec des données Python.''',
        'url': 'https://jinja.palletsprojects.com',
        'categorie': 'Web',
        'auteur': 'Armin Ronacher',
        'tags': 'jinja2,templates,html,flask'
    },
    {
        'titre': 'Bases de Données avec SQLAlchemy',
        'description': 'ORM pour Python',
        'contenu': '''SQLAlchemy est un ORM (Object-Relational Mapping) pour Python.
        Convertit les classes Python en tables de base de données.
        Supporte MySQL, PostgreSQL, SQLite et autres.''',
        'url': 'https://sqlalchemy.org',
        'categorie': 'Bases de Données',
        'auteur': 'Mike Bayer',
        'tags': 'sqlalchemy,orm,base de données,python'
    },
    {
        'titre': 'API REST avec Flask',
        'description': 'Créer des API JSON',
        'contenu': '''REST (Representational State Transfer) est un style pour les APIs.
        Utilise HTTP methods (GET, POST, PUT, DELETE) sur des ressources.
        Retourne généralement du JSON pour l\'échange de données.''',
        'url': 'https://flask.palletsprojects.com/json',
        'categorie': 'Web',
        'auteur': 'REST Community',
        'tags': 'rest,api,json,web,flask'
    },
    {
        'titre': 'Authentification en Flask',
        'description': 'Protéger vos applications',
        'contenu': '''L\'authentification identifie les utilisateurs. L\'autorisation contrôle l\'accès.
        Sessions: stockent les données utilisateur côté serveur.
        Tokens: JWT pour les APIs. Mots de passe: toujours hasher avec bcrypt.''',
        'url': 'https://flask.palletsprojects.com/security',
        'categorie': 'Web',
        'auteur': 'Security Best Practices',
        'tags': 'flask,authentification,sécurité,users'
    },
    {
        'titre': 'JavaScript Moderne (ES6+)',
        'description': 'JavaScript côté client moderne',
        'contenu': '''ES6 (EcmaScript 2015) a amené des améliorations majeures: arrow functions, classes, promises.
        const/let pour les variables. Destructuring pour extraire les données.
        async/await pour la programmation asynchrone.''',
        'url': 'https://developer.mozilla.org/javascript',
        'categorie': 'Frontend',
        'auteur': 'MDN',
        'tags': 'javascript,es6,frontend,web'
    },
    {
        'titre': 'DOM et Manipulation du DOM',
        'description': 'Contrôler le HTML avec JavaScript',
        'contenu': '''Le DOM (Document Object Model) représente la structure HTML.
        Sélecteurs: getElementById, querySelector, querySelectorAll.
        Opérations: créer, modifier, supprimer des éléments dynamiquement.''',
        'url': 'https://developer.mozilla.org/dom',
        'categorie': 'Frontend',
        'auteur': 'Web Standards',
        'tags': 'javascript,dom,frontend,html'
    },
    {
        'titre': 'Fetch API et Requêtes AJAX',
        'description': 'Communication asynchrone sans recharger',
        'contenu': '''Fetch permet de faire des requêtes HTTP en JavaScript.
        Remplace XMLHttpRequest. Retourne une Promise.
        Usage: fetch(url).then(response => response.json()).then(data => console.log(data))''',
        'url': 'https://developer.mozilla.org/fetch',
        'categorie': 'Frontend',
        'auteur': 'Web Standards',
        'tags': 'javascript,fetch,ajax,api,promises'
    },
    {
        'titre': 'Événements JavaScript',
        'description': 'Réagir aux interactions utilisateur',
        'contenu': '''Les événements se produisent quand l\'utilisateur interagit.
        Types: click, submit, input, change, keydown, mouseover.
        Gestion: addEventListener(), onclick, onsubmit attributes.''',
        'url': 'https://developer.mozilla.org/events',
        'categorie': 'Frontend',
        'auteur': 'Web APIs',
        'tags': 'javascript,événements,interactivité'
    },
    {
        'titre': 'CSS Avancé et Flexbox',
        'description': 'Layouts modernes avec CSS',
        'contenu': '''Flexbox permet de créer des layouts flexibles et responsifs.
        Propriétés principales: display: flex, justify-content, align-items, flex-direction.
        Alternative plus simple que Grid pour layouts simples.''',
        'url': 'https://developer.mozilla.org/css',
        'categorie': 'Frontend',
        'auteur': 'CSS Working Group',
        'tags': 'css,flexbox,layout,design'
    },
    {
        'titre': 'CSS Grid',
        'description': 'Créer des grilles bidimensionnelles',
        'contenu': '''Grid permet de créer des layouts en grille complexes.
        Propriétés: display: grid, grid-template-columns, grid-template-rows, gap.
        Plus puissant que Flexbox pour les layouts complexes.''',
        'url': 'https://developer.mozilla.org/css-grid',
        'categorie': 'Frontend',
        'auteur': 'CSS Working Group',
        'tags': 'css,grid,layout,design'
    },
    {
        'titre': 'Responsive Web Design',
        'description': 'Sites qui s\'adaptent à tous les écrans',
        'contenu': '''Le responsive design fait que le site s\'adapte aux appareils.
        Media queries: @media (max-width: 768px) { ... }
        Mobile-first: concevoir pour mobile en premier.''',
        'url': 'https://developer.mozilla.org/responsive',
        'categorie': 'Frontend',
        'auteur': 'Web Best Practices',
        'tags': 'responsive,css,mobile,design'
    },

    # === BASES DE DONNÉES (10 docs) ===
    {
        'titre': 'Introduction à MySQL',
        'description': 'Système de gestion de base de données relationnelle',
        'contenu': '''MySQL est un système de base de données SQL populaire et open-source.
        Stocke les données en tables avec des lignes et colonnes.
        Utilise SQL pour interroger et modifier les données.''',
        'url': 'https://mysql.com',
        'categorie': 'Bases de Données',
        'auteur': 'MySQL Team',
        'tags': 'mysql,sql,bases de données,rdbms'
    },
    {
        'titre': 'SQL: SELECT et WHERE',
        'description': 'Récupérer des données avec SQL',
        'contenu': '''SELECT récupère des données. WHERE filtre les lignes.
        Syntaxe: SELECT colonne FROM table WHERE condition.
        Opérateurs: =, !=, <, >, <=, >=, IN, LIKE, AND, OR.''',
        'url': 'https://mysql.com/sql-select',
        'categorie': 'Bases de Données',
        'auteur': 'SQL Basics',
        'tags': 'sql,select,where,queries'
    },
    {
        'titre': 'SQL: JOIN pour Combiner des Tables',
        'description': 'Associer les données de plusieurs tables',
        'contenu': '''JOIN combine les lignes de plusieurs tables basé sur une condition.
        Types: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.
        Permet de récupérer des données liées de plusieurs tables.''',
        'url': 'https://mysql.com/sql-join',
        'categorie': 'Bases de Données',
        'auteur': 'SQL Advanced',
        'tags': 'sql,join,relations,queriess'
    },
    {
        'titre': 'SQL: INSERT, UPDATE, DELETE',
        'description': 'Modifier les données',
        'contenu': '''INSERT ajoute de nouvelles lignes. UPDATE modifie les existantes. DELETE supprime.
        INSERT: INSERT INTO table (cols) VALUES (vals).
        UPDATE: UPDATE table SET col=val WHERE condition.''',
        'url': 'https://mysql.com/sql-modify',
        'categorie': 'Bases de Données',
        'auteur': 'SQL DML',
        'tags': 'sql,insert,update,delete,dml'
    },
    {
        'titre': 'Créer une Structure de Base de Données',
        'description': 'Concevoir des tables et schémas',
        'contenu': '''CREATE TABLE définit une nouvelle table avec colonnes et types.
        Clés primaires: identifient les lignes. Clés étrangères: créent des relations.
        Indexes: accélèrent les requêtes. Contraintes: assurent la validité.''',
        'url': 'https://mysql.com/sql-create',
        'categorie': 'Bases de Données',
        'auteur': 'Database Design',
        'tags': 'sql,create,tables,schema,indexes'
    },
    {
        'titre': 'Recherche FULLTEXT en MySQL',
        'description': 'Recherche textuelle avancée',
        'contenu': '''FULLTEXT indexes permettent une recherche textuelle rapide.
        MATCH() AGAINST() pour les requêtes full-text.
        Modes: natural language, boolean, query expansion.''',
        'url': 'https://mysql.com/fulltext',
        'categorie': 'Bases de Données',
        'auteur': 'MySQL Search',
        'tags': 'mysql,fulltext,recherche,indexes'
    },
    {
        'titre': 'Transactions et ACID',
        'description': 'Assurer la cohérence des données',
        'contenu': '''Transactions groupent les opérations en unités atomiques.
        ACID: Atomicité, Cohérence, Isolation, Durabilité.
        BEGIN, COMMIT, ROLLBACK pour contrôler les transactions.''',
        'url': 'https://mysql.com/transactions',
        'categorie': 'Bases de Données',
        'auteur': 'Database Theory',
        'tags': 'transactions,acid,database,integrity'
    },
    {
        'titre': 'Performance et Optimisation SQL',
        'description': 'Rendre les requêtes plus rapides',
        'contenu': '''EXPLAIN montre comment une requête est exécutée.
        Utilisez les indexes sur les colonnes fréquemment recherchées.
        Normalisez les données pour éviter la redondance.''',
        'url': 'https://mysql.com/optimization',
        'categorie': 'Bases de Données',
        'auteur': 'Performance Tips',
        'tags': 'mysql,performance,optimization,indexes'
    },
    {
        'titre': 'Sauvegarder et Restaurer MySQL',
        'description': 'Protéger vos données',
        'contenu': '''mysqldump exporte une base de données en fichier SQL.
        Sauvegarde: mysqldump -u user -p db > backup.sql.
        Restauration: mysql -u user -p db < backup.sql.''',
        'url': 'https://mysql.com/backup',
        'categorie': 'Bases de Données',
        'auteur': 'Database Administration',
        'tags': 'mysql,backup,restore,administration'
    },

    # === MACHINE LEARNING (12 docs) ===
    {
        'titre': 'Introduction au Machine Learning',
        'description': 'Les machines apprennent à partir de données',
        'contenu': '''Le machine learning crée des modèles que les machines apprennent à partir de données.
        Types: supervisé (avec étiquettes), non-supervisé (sans étiquettes), par renforcement.
        Applications: reconnaissance d\'images, traduction, recommandations.''',
        'url': 'https://ml.org/intro',
        'categorie': 'Machine Learning',
        'auteur': 'AI Academy',
        'tags': 'machine-learning,ai,intelligence-artificielle'
    },
    {
        'titre': 'Apprentissage Supervisé',
        'description': 'Apprentissage avec des données étiquetées',
        'contenu': '''L\'apprentissage supervisé utilise des données d\'entraînement étiquetées.
        Régression: prédire une valeur continue. Classification: prédire une classe.
        Exemples: prédire le prix, classer le spam.''',
        'url': 'https://ml.org/supervised',
        'categorie': 'Machine Learning',
        'auteur': 'ML Techniques',
        'tags': 'machine-learning,supervised,regression,classification'
    },
    {
        'titre': 'Arbres de Décision',
        'description': 'Algorithme simple et interprétable',
        'contenu': '''Les arbres de décision divisent les données en conditions successives.
        Utilisent des features pour faire de meilleures décisions.
        Avantages: faciles à comprendre. Inconvénients: tendance à surfit.''',
        'url': 'https://ml.org/decision-trees',
        'categorie': 'Machine Learning',
        'auteur': 'ML Algorithms',
        'tags': 'machine-learning,decision-trees,classification'
    },
    {
        'titre': 'Forêts Aléatoires',
        'description': 'Assemblage d\'arbres pour de meilleures prédictions',
        'contenu': '''Les forêts aléatoires combinent plusieurs arbres de décision.
        Réduisent le surfit grâce à l\'aléatoire et à l\'ensemble.
        Très performantes et robustes.''',
        'url': 'https://ml.org/random-forests',
        'categorie': 'Machine Learning',
        'auteur': 'ML Methods',
        'tags': 'machine-learning,random-forests,ensemble'
    },
    {
        'titre': 'Support Vector Machines (SVM)',
        'description': 'Classification précise avec hyperplans',
        'contenu': '''Les SVM trouvent l\'hyperplan optimal pour séparer les classes.
        Utilisent des kernels pour les données non-linéaires.
        Très efficaces pour la classification binaire et multi-classe.''',
        'url': 'https://ml.org/svm',
        'categorie': 'Machine Learning',
        'auteur': 'ML Theory',
        'tags': 'machine-learning,svm,classification'
    },
    {
        'titre': 'Réseaux de Neurones',
        'description': 'Inspirés par le cerveau humain',
        'contenu': '''Les réseaux de neurones sont des modèles inspirés par le cerveau.
        Couches: input, hidden, output. Activation: ReLU, Sigmoid, Softmax.
        Apprentissage: backpropagation ajuste les poids.''',
        'url': 'https://ml.org/neural-networks',
        'categorie': 'Deep Learning',
        'auteur': 'Deep Learning Institute',
        'tags': 'neural-networks,deep-learning,ai'
    },
    {
        'titre': 'Deep Learning et Tensorflow',
        'description': 'Frameworks pour les réseaux de neurones',
        'contenu': '''TensorFlow est une librairie open-source de Google pour le deep learning.
        Keras fournit une API simple. PyTorch est une alternative populaire.
        Utilisés pour la vision par ordinateur et le traitement du langage.''',
        'url': 'https://tensorflow.org',
        'categorie': 'Deep Learning',
        'auteur': 'Google AI',
        'tags': 'tensorflow,deep-learning,neural-networks,ai'
    },
    {
        'titre': 'Traitement du Langage Naturel (NLP)',
        'description': 'Comprendre et générer du texte',
        'contenu': '''Le NLP permet aux machines de comprendre le langage humain.
        Techniques: tokenization, stemming, TF-IDF, word embeddings.
        Applications: traduction, sentiment analysis, chatbots.''',
        'url': 'https://nlp.org',
        'categorie': 'Machine Learning',
        'auteur': 'NLP Community',
        'tags': 'nlp,natural-language-processing,text,ai'
    },
    {
        'titre': 'Word Embeddings et Word2Vec',
        'description': 'Représenter les mots en vecteurs',
        'contenu': '''Word2Vec convertit les mots en vecteurs numériques (embeddings).
        Modèles: Skip-gram et CBOW. Capture les relations sémantiques.
        Exemple: vecteur(\"king\") - vecteur(\"man\") + vecteur(\"woman\") ≈ vecteur(\"queen\").''',
        'url': 'https://nlp.org/word2vec',
        'categorie': 'Machine Learning',
        'auteur': 'NLP Advances',
        'tags': 'nlp,embeddings,word2vec,semantics'
    },
    {
        'titre': 'Clustering et K-means',
        'description': 'Apprentissage non-supervisé pour grouper les données',
        'contenu': '''Le clustering groupe des données similaires sans étiquettes.
        K-means: divise les données en k clusters. Pas besoin de labels.
        Utilisé pour la segmentation, recommandations, découverte de patterns.''',
        'url': 'https://ml.org/clustering',
        'categorie': 'Machine Learning',
        'auteur': 'Unsupervised Learning',
        'tags': 'machine-learning,clustering,k-means,unsupervised'
    },
    {
        'titre': 'Validation et Evaluation de Modèles',
        'description': 'Mesurer la performance',
        'contenu': '''Train/validation/test split: divise les données.
        Métriques: accuracy, precision, recall, F1-score, AUC.
        Cross-validation: valide avec différents splits.''',
        'url': 'https://ml.org/evaluation',
        'categorie': 'Machine Learning',
        'auteur': 'Validation Methods',
        'tags': 'machine-learning,evaluation,metrics,validation'
    },

    # === ARCHITECTURE ET DESIGN (10 docs) ===
    {
        'titre': 'Architecture Logicielle',
        'description': 'Concevoir des systèmes complexes',
        'contenu': '''L\'architecture est la structure high-level d\'un logiciel.
        Couches: présentation, métier, données.
        Patterns: MVC, MVVM, clean architecture.''',
        'url': 'https://architecture.org',
        'categorie': 'Architecture',
        'auteur': 'Software Design',
        'tags': 'architecture,design,patterns,software'
    },
    {
        'titre': 'Design Patterns: Singleton',
        'description': 'Un seul instance d\'une classe',
        'contenu': '''Le pattern Singleton assure qu\'une classe n\'a qu\'une instance.
        Utile pour les configurations, logs, connexions.
        Implémentation: constructor privé, getInstance() statique.''',
        'url': 'https://patterns.org/singleton',
        'categorie': 'Design Patterns',
        'auteur': 'Gang of Four',
        'tags': 'design-patterns,singleton,oop'
    },
    {
        'titre': 'Design Patterns: Factory',
        'description': 'Créer des objets sans spécifier les classes',
        'contenu': '''Le pattern Factory encapsule la création d\'objets.
        Avantages: flexibilité, découplage.
        Utilisé dans les frameworks pour créer des composants.''',
        'url': 'https://patterns.org/factory',
        'categorie': 'Design Patterns',
        'auteur': 'Gang of Four',
        'tags': 'design-patterns,factory,creational'
    },
    {
        'titre': 'SOLID: Single Responsibility',
        'description': 'Une classe, une responsabilité',
        'contenu': '''SRP: une classe doit avoir une seule raison de changer.
        Rend le code plus testable et maintenable.
        Évite les classes \"dieu\" qui font trop de choses.''',
        'url': 'https://solid.org/srp',
        'categorie': 'Design Principles',
        'auteur': 'Robert Martin',
        'tags': 'solid,design,principles,single-responsibility'
    },
    {
        'titre': 'SOLID: Dependency Injection',
        'description': 'Injecter les dépendances plutôt que de les créer',
        'contenu': '''DIP: les classes dépendent des abstractions, pas des concrétions.
        Permet de changer les implémentations facilement.
        Dependency Injection containers gèrent les dépendances.''',
        'url': 'https://solid.org/dip',
        'categorie': 'Design Principles',
        'auteur': 'Robert Martin',
        'tags': 'solid,design,dependency-injection,ioc'
    },
    {
        'titre': 'Microservices',
        'description': 'Architecture distribuée de services petits et indépendants',
        'contenu': '''Microservices sont de petits services indépendants et déployables.
        Chaque service gère un domaine métier. Communication via APIs.
        Avantages: scalabilité, flexibilité. Complexité: distribution.''',
        'url': 'https://microservices.org',
        'categorie': 'Architecture',
        'auteur': 'Cloud Architecture',
        'tags': 'microservices,architecture,distributed,services'
    },
    {
        'titre': 'Conteneurisation avec Docker',
        'description': 'Empaque les applications dans des conteneurs',
        'contenu': '''Docker crée des conteneurs légers et portables.
        Dockerfile définit l\'image. docker run lance un conteneur.
        Avantage: \"ça marche sur ma machine\" n\'existe plus.''',
        'url': 'https://docker.com',
        'categorie': 'DevOps',
        'auteur': 'Docker Team',
        'tags': 'docker,containers,devops,deployment'
    },
    {
        'titre': 'Orchestration avec Kubernetes',
        'description': 'Gérer des conteneurs à grande échelle',
        'contenu': '''Kubernetes automatise le déploiement et les opérations.
        Pods, Services, Deployments, StatefulSets.
        Utilisé dans les productions massives.''',
        'url': 'https://kubernetes.io',
        'categorie': 'DevOps',
        'auteur': 'Cloud Native Computing',
        'tags': 'kubernetes,containers,orchestration,devops'
    },
    {
        'titre': 'CI/CD: Intégration Continue',
        'description': 'Automatiser la construction et les tests',
        'contenu': '''CI/CD automatise l\'intégration, test et déploiement du code.
        Pipelines: code -> build -> test -> deploy.
        Outils: Jenkins, GitLab CI, GitHub Actions, CircleCI.''',
        'url': 'https://cicd.org',
        'categorie': 'DevOps',
        'auteur': 'DevOps Community',
        'tags': 'ci-cd,devops,automation,deployment'
    },

    # === OUTILS ET TECHNOLOGIES (10 docs) ===
    {
        'titre': 'Git et Contrôle de Version',
        'description': 'Gérer l\'historique du code',
        'contenu': '''Git track les changements du code. Branches pour travailler en parallèle.
        Commits enregistrent les changements. Merges combine les branches.
        GitHub héberge les repos et facilite la collaboration.''',
        'url': 'https://git-scm.com',
        'categorie': 'Outils',
        'auteur': 'Linus Torvalds',
        'tags': 'git,version-control,github,collaboration'
    },
    {
        'titre': 'Linux et Ligne de Commande',
        'description': 'Travailler avec le terminal',
        'contenu': '''Linux est un système d\'exploitation libre. Terminal permet d\'exécuter des commandes.
        Commandes clés: ls, cd, mkdir, cp, rm, grep, find.
        Shell scripts automatisent les tâches répétitives.''',
        'url': 'https://linux.org',
        'categorie': 'Outils',
        'auteur': 'Linux Community',
        'tags': 'linux,terminal,shell,commands'
    },
    {
        'titre': 'Gestion de Paquets npm',
        'description': 'Installer et gérer les librairies JavaScript',
        'contenu': '''npm (Node Package Manager) installe les librairies JavaScript.
        package.json liste les dépendances. npm install les télécharge.
        Scripts npm: \"start\", \"test\", \"build\" pour l\'automatisation.''',
        'url': 'https://npmjs.com',
        'categorie': 'Outils',
        'auteur': 'npm Team',
        'tags': 'npm,javascript,package-management,nodejs'
    },
    {
        'titre': 'Environnements virtuels Python',
        'description': 'Isoler les dépendances par projet',
        'contenu': '''Virtualenv crée un environnement Python isolé.
        Chaque projet a sa propre version de Python et librairies.
        requirements.txt liste les dépendances. pip install les installe.''',
        'url': 'https://python.org/venv',
        'categorie': 'Outils',
        'auteur': 'Python Foundation',
        'tags': 'python,virtualenv,dependencies,environment'
    },
    {
        'titre': 'Linting et Formatage de Code',
        'description': 'Code propre et cohérent',
        'contenu': '''Linters vérifient les erreurs et le style. Formateurs corrigent automatiquement.
        Python: pylint, flake8, black. JavaScript: eslint, prettier.
        Intégrez dans vos workflows pour une qualité consistante.''',
        'url': 'https://linting.org',
        'categorie': 'Outils',
        'auteur': 'Code Quality',
        'tags': 'linting,formatting,code-quality,tools'
    },
    {
        'titre': 'Tests Unitaires et Mocking',
        'description': 'Tester chaque fonction individuellement',
        'contenu': '''Les tests unitaires testent les fonctions isolément.
        Frameworks: pytest (Python), Jest (JavaScript), JUnit (Java).
        Mocking simule les dépendances pour tester en isolation.''',
        'url': 'https://testing.org',
        'categorie': 'Outils',
        'auteur': 'Testing Best Practices',
        'tags': 'testing,unit-tests,mocking,quality'
    },
    {
        'titre': 'Déboguer et Profiler',
        'description': 'Trouver et corriger les bugs',
        'contenu': '''Debuggers permettent de mettre des breakpoints et inspecter les variables.
        Profilers mesurent la performance et l\'usage mémoire.
        Outils: pdb (Python), DevTools (JavaScript), profilers spécialisés.''',
        'url': 'https://debugging.org',
        'categorie': 'Outils',
        'auteur': 'Developer Tools',
        'tags': 'debugging,profiling,performance,tools'
    },
    {
        'titre': 'API Documentation avec Swagger/OpenAPI',
        'description': 'Documenter les APIs RESTful',
        'contenu': '''OpenAPI (Swagger) définit les APIs de manière standardisée.
        Génère automatiquement la documentation et les clients.
        Permet la collaboration entre frontend et backend.''',
        'url': 'https://swagger.io',
        'categorie': 'Outils',
        'auteur': 'OpenAPI Initiative',
        'tags': 'api,documentation,swagger,openapi'
    },
    {
        'titre': 'Caching Strategies',
        'description': 'Accélérer les applications avec le cache',
        'contenu': '''Cache stocke les données fréquemment accédées.
        Types: Browser cache, CDN cache, Database cache, Application cache.
        Outils: Redis, Memcached pour le cache distribué.''',
        'url': 'https://caching.org',
        'categorie': 'Performance',
        'auteur': 'Performance Engineering',
        'tags': 'caching,performance,optimization,redis'
    },
    # === IMAGES ET VIDEOS DE TEST ===
    {
        'titre': 'Logo Python Officiel',
        'description': 'Le logo officiel du langage Python avec le serpent emblématique',
        'contenu': '''Image du logo Python officiel. Le logo représente deux serpents entrelacés formant la lettre P majuscule. Couleurs bleu et jaune caractéristiques. Utilisé pour représenter le langage de programmation Python dans la documentation officielle et les présentations.''',
        'url': 'https://python.org/static/img/python-logo.png',
        'categorie': 'image',
        'auteur': 'Python Foundation',
        'tags': 'python,logo,image,officiel,serpent,bleu,jaune'
    },
    {
        'titre': 'Logo JavaScript ES6+ Features Illustration',
        'description': 'Illustration des nouvelles fonctionnalités ES6 de JavaScript',
        'contenu': '''Image illustrant les nouvelles fonctionnalités de JavaScript ES6+. Montre les arrow functions, classes, promises, async/await, destructuring. Utilisé dans les tutoriels et présentations sur JavaScript moderne.''',
        'url': 'https://developer.mozilla.org/js-es6-features.jpg',
        'categorie': 'image',
        'auteur': 'MDN Web Docs',
        'tags': 'javascript,es6,features,illustration,tutoriel,moderne,async,promises'
    },
    {
        'titre': 'Diagramme Architecture MVC',
        'description': 'Schéma explicatif de l\'architecture Modèle-Vue-Contrôleur',
        'contenu': '''Diagramme illustrant l'architecture MVC (Model-View-Controller). Montre les interactions entre le modèle de données, la vue utilisateur et le contrôleur. Flèches montrant le flux de données et les responsabilités de chaque composant.''',
        'url': 'https://architecture.org/mvc-diagram.png',
        'categorie': 'image',
        'auteur': 'Software Architecture Patterns',
        'tags': 'architecture,mvc,diagramme,schema,modele,vue,controleur,design-patterns'
    },
    {
        'titre': 'Tutoriel Python pour Débutants - Vidéo Complète',
        'description': 'Vidéo tutoriel complet pour apprendre Python de zéro en 2 heures',
        'contenu': '''Vidéo tutoriel complète pour apprendre Python depuis le début. Couvre l'installation, les variables, les boucles, les fonctions, les classes. Durée: 2h15. Niveau débutant à intermédiaire. Inclut des exercices pratiques.''',
        'url': 'https://youtube.com/watch?v=example-python-tutorial.mp4',
        'categorie': 'video',
        'auteur': 'Python Learning Channel',
        'tags': 'python,tutoriel,video,debutant,apprentissage,programmation,exercices,2h15,complet'
    },
    {
        'titre': 'Démonstration Live Coding JavaScript ES6 Features',
        'description': 'Session de live coding montrant les fonctionnalités modernes de JavaScript ES6+',
        'contenu': '''Vidéo de démonstration en direct montrant l'utilisation des fonctionnalités ES6 de JavaScript. Code en temps réel avec explications. Couvre les arrow functions, template literals, destructuring, spread operator, async/await.''',
        'url': 'https://youtube.com/watch?v=js-es6-live-demo.mp4',
        'categorie': 'video',
        'auteur': 'JavaScript Masters',
        'tags': 'javascript,es6,live-coding,demonstration,features,moderne,async,await,template-literals,arrow-functions'
    },
    {
        'titre': 'Architecture Microservices - Explication Visuelle 3D',
        'description': 'Animation 3D expliquant l\'architecture de microservices avec exemples concrets',
        'contenu': '''Vidéo d'animation 3D expliquant l'architecture de microservices. Montre comment les services communiquent, la scalabilité, les avantages et inconvénients. Exemples avec containers Docker et orchestration Kubernetes.''',
        'url': 'https://architecture-videos.com/microservices-3d.mp4',
        'categorie': 'video',
        'auteur': 'Cloud Architecture Visuals',
        'tags': 'microservices,architecture,3d,animation,docker,kubernetes,scalabilite,containers,services,orchestration'
    },]

def populate_database():
    """Insère tous les documents dans la base de données"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔄 Suppression des documents existants...")
        cursor.execute("DELETE FROM documents")
        connection.commit()
        
        print("📝 Insertion des documents...")
        
        inserted = 0
        base_date = datetime.now() - timedelta(days=365)
        
        for doc in DOCUMENTS:
            random_days = random.randint(0, 365)
            pub_date = base_date + timedelta(days=random_days)
            
            sql = """
            INSERT INTO documents 
            (titre, description, contenu, url, categorie, auteur, tags, date_publication)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                doc['titre'],
                doc['description'],
                doc['contenu'],
                doc.get('url', ''),
                doc['categorie'],
                doc['auteur'],
                doc['tags'],
                pub_date
            )
            
            cursor.execute(sql, values)
            inserted += 1
            
            if inserted % 10 == 0:
                print(f"  ✓ {inserted}/{len(DOCUMENTS)} documents insérés...")
        
        connection.commit()
        
        # Vérifier le total
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]
        
        print("\n" + "="*70)
        print(f"✅ SUCCÈS! {inserted} nouveaux documents insérés")
        print(f"📊 Total: {total} documents en base de données")
        print("="*70)
        print("\n🎯 Prêt à tester!")
        print("   → http://localhost/Moteur-recherche/frontend/google.html")
        print("   → Cherchez: Python, Web, Machine Learning, Flask, Database, etc.")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ ERREUR: {err}")
        print("\nAssurez-vous que:")
        print("  1. La base 'moteur_recherche' existe")
        print("  2. MySQL fonctionne")
        print("  3. Le schéma a été importé (database/schema_v2.sql)")
        return False
    
    return True

if __name__ == "__main__":
    populate_database()
