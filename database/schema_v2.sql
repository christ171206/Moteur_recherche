-- =====================================================
-- MOTEUR DE RECHERCHE - Base de données v2 (Pro)
-- =====================================================

DROP DATABASE IF EXISTS moteur_recherche;
CREATE DATABASE IF NOT EXISTS moteur_recherche CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE moteur_recherche;

-- =====================================================
-- TABLE : Documents
-- =====================================================
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    description TEXT,
    contenu LONGTEXT NOT NULL,
    url VARCHAR(512),
    categorie VARCHAR(100) DEFAULT 'General',
    tags VARCHAR(512),
    auteur VARCHAR(255),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    date_publication DATE,
    vue INT DEFAULT 0,
    pertinence_score FLOAT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    metadata JSON,
    
    -- Indexes pour performance
    INDEX idx_categorie (categorie),
    INDEX idx_date (date_publication),
    INDEX idx_active (active),
    FULLTEXT INDEX ft_titre (titre),
    FULLTEXT INDEX ft_contenu (contenu),
    FULLTEXT INDEX ft_titre_contenu (titre, contenu),
    FULLTEXT INDEX ft_all (titre, description, contenu)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLE : Statistiques de recherche
-- =====================================================
CREATE TABLE search_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text VARCHAR(255),
    nb_resultats INT,
    document_clicked INT,
    date_recherche TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duree_requete_ms INT,
    
    FULLTEXT INDEX ft_query (query_text),
    INDEX idx_date (date_recherche)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLE : Historique de vues
-- =====================================================
CREATE TABLE document_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    date_vue TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_query VARCHAR(255),
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document (document_id),
    INDEX idx_date (date_vue)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLE : Index TF-IDF (Cache)
-- =====================================================
CREATE TABLE term_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    term VARCHAR(255),
    document_id INT NOT NULL,
    tf FLOAT,  -- Term Frequency
    idf FLOAT, -- Inverse Document Frequency
    score FLOAT,
    
    UNIQUE KEY unique_term_doc (term, document_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_term (term)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- DONNÉES DE TEST
-- =====================================================
INSERT INTO documents (titre, description, contenu, categorie, tags, auteur, date_publication) VALUES
('Introduction à Python', 
 'Les bases du langage de programmation Python',
 'Python est un langage de programmation interprété créé par Guido van Rossum en 1991. Il est très populaire pour l''apprentissage et le développement rapide d''applications. Python supporte la programmation orientée objet, la programmation fonctionnelle et de nombreuses autres fonctionnalités.',
 'Programmation', 'python,langages,tutoriel', 'John Doe', '2025-01-15'),

('Bases de données MySQL',
 'Gestion des données avec MySQL',
 'MySQL est un système de gestion de bases de données relationnelles open-source. Il est largement utilisé dans les applications web, particulièrement avec PHP et Apache. MySQL offre des performances élevées et une grande fiabilité pour le stockage des données.',
 'Bases de données', 'mysql,sql,base-donnees,tutoriel', 'Jane Smith', '2025-01-20'),

('API REST avec Flask',
 'Créer des services web avec Flask',
 'Flask est un framework web microservices Python léger et flexible. Il permet de créer rapidement des API REST sans dépendances lourdes. Flask est très flexible et peut être utilisé pour créer des applications complexes avec peu de code.',
 'Web Development', 'flask,python,api,rest', 'Bob Johnson', '2025-02-01'),

('JavaScript et DOM',
 'Manipulation du DOM avec JavaScript',
 'Le Document Object Model (DOM) est une interface de programmation pour les documents HTML et XML. JavaScript permet de modifier dynamiquement le contenu, la structure et le style d''une page web. Comprendre le DOM est essentiel pour créer des applications web interactives.',
 'Web Development', 'javascript,dom,web,frontend', 'Alice Brown', '2025-02-05'),

('Architecture des Moteurs de Recherche',
 'Comment fonctionnent les moteurs de recherche modernes',
 'Un moteur de recherche indexe des millions de pages web et utilise des algorithmes sophistiqués pour classer les résultats. Les composants clés incluent le crawler, l''indexeur, le ranking algoritm et l''interface de recherche. Le TF-IDF et BM25 sont des algorithmes classiques pour calculer la pertinence.',
 'Informatique', 'moteur-recherche,seo,algorithmes,indexation', 'Charlie Davis', '2025-02-10'),

('Sécurité Web - OWASP Top 10',
 'Les 10 principales vulnérabilités web',
 'OWASP identifie les 10 principales vulnerabilités de sécurité des applications web. Elles incluent l''injection SQL, l''authentification faible, les XSS, le CSRF et autres. Chaque développeur doit connaître ces vulnerabilités pour créer des applications sécurisées.',
 'Sécurité', 'owasp,securite,web,vulnerabilites', 'David Wilson', '2025-02-15'),

('Responsive Design avec CSS',
 'Créer des sites adaptatifs avec CSS3',
 'Le responsive design permet à un site web de s''adapter à différentes tailles d''écran. Les media queries CSS permettent de définir des règles différentes pour le mobile, la tablette et le desktop. Vue.js et React facilitent la création d''interfaces réactives et performantes.',
 'Web Design', 'css,responsive,design,mobile-first', 'Eve Taylor', '2025-02-20'),

('Git et Contrôle de Version',
 'Maîtriser Git pour la gestion de projets',
 'Git est un système de contrôle de version décentralisé créé par Linus Torvalds. Il permet à plusieurs développeurs de collaborer efficacement sur un même projet. Les concepts clés incluent les commits, branches, merges et le workflow git-flow.',
 'DevOps', 'git,version-control,github,collaboration', 'Frank Miller', '2025-02-25'),

('Docker et Containerisation',
 'Déployer des applications avec Docker',
 'Docker permet de containeriser les applications pour un déploiement cohérent. les conteneurs Docker incluent l''application et toutes ses dépendances. Docker Compose permet d''orchestrer plusieurs conteneurs. Docker est devenu un standard industriel pour le DevOps.',
 'DevOps', 'docker,containers,devops,deployment', 'Grace Lee', '2025-03-01'),

('Machine Learning avec Python',
 'Introduction au ML avec scikit-learn',
 'Le Machine Learning permet aux ordinateurs d''apprendre à partir de données. Les bibliothèques Python comme scikit-learn et TensorFlow facilitent l''implémentation d''algorithmes ML. Les applications incluent la classification, la régression, le clustering et les réseaux de neurones.',
 'Intelligence Artificielle', 'machine-learning,python,ai,data-science', 'Henry Davis', '2025-03-05');

-- Afficher le nombre d'enregistrements
SELECT COUNT(*) as total_documents FROM documents;
