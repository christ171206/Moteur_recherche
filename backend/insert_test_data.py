#!/usr/bin/env python
"""Script pour ajouter des données de test à la base de données"""

import sys
sys.path.insert(0, '.')

from services import DatabaseService

def insert_test_data():
    """Insère 10 documents de test"""
    
    documents = [
        {
            'titre': 'Python Programming Guide',
            'description': 'Complete guide to Python programming',
            'contenu': 'Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including object-oriented, imperative, functional, and procedural programming. Python was created by Guido van Rossum and first released in 1991.',
            'categorie': 'Programming',
            'tags': 'python,programming,tutorial',
            'auteur': 'John Programmer',
            'url': 'https://python.org',
            'date_publication': '2025-01-15'
        },
        {
            'titre': 'Web Development with Flask',
            'description': 'Build web applications using Flask framework',
            'contenu': 'Flask is a lightweight WSGI web application framework written in Python. It is designed to make getting started quick and easy. Flask provides tools, libraries and technologies that allow you to build web applications efficiently.',
            'categorie': 'Web',
            'tags': 'flask,web,python,framework',
            'auteur': 'Jane Developer',
            'url': 'https://flask.palletsprojects.com',
            'date_publication': '2025-02-10'
        },
        {
            'titre': 'Machine Learning Fundamentals',
            'description': 'Introduction to machine learning concepts',
            'contenu': 'Machine Learning is a subset of Artificial Intelligence that provides systems the ability to automatically learn and improve from experience. ML focuses on algorithms that can learn patterns from data and make predictions without being explicitly programmed.',
            'categorie': 'AI',
            'tags': 'machine-learning,ai,data-science',
            'auteur': 'Dr. AI Expert',
            'url': 'https://ml-academy.com',
            'date_publication': '2025-01-20'
        },
        {
            'titre': 'Database Design Best Practices',
            'description': 'Learn proper database design principles',
            'contenu': 'Database design is the process of producing a detailed data model of a database. This includes logical and physical design choices needed for efficient data storage and retrieval. Learning normalization and schema design is essential.',
            'categorie': 'Database',
            'tags': 'sql,database,design,normalization',
            'auteur': 'SQL Master',
            'url': 'https://db-design.org',
            'date_publication': '2025-02-05'
        },
        {
            'titre': 'JavaScript for Web Development',
            'description': 'Master JavaScript programming language',
            'contenu': 'JavaScript is a programming language commonly used to create interactive effects within web browsers. It is dynamic and supports object-oriented, functional, and procedural programming paradigms. Modern JavaScript is powerful and versatile.',
            'categorie': 'Web',
            'tags': 'javascript,web,frontend,es6',
            'auteur': 'Web Expert',
            'url': 'https://javascript.info',
            'date_publication': '2025-01-25'
        },
        {
            'titre': 'Data Structures and Algorithms',
            'description': 'Core computer science fundamentals',
            'contenu': 'Data structures are ways to organize and store data efficiently. Understanding arrays, linked lists, trees, graphs, and hash tables is crucial for writing efficient software. Algorithms operate on data structures to solve problems optimally.',
            'categorie': 'ComputerScience',
            'tags': 'data-structures,algorithms,cs,complexity',
            'auteur': 'CS Teacher',
            'url': 'https://cs-academy.org',
            'date_publication': '2025-02-01'
        },
        {
            'titre': 'REST API Design Patterns',
            'description': 'Design and build REST APIs correctly',
            'contenu': 'REST stands for Representational State Transfer. It is an architectural style for designing networked applications. REST APIs use HTTP requests to perform CRUD operations on resources identified by URLs.',
            'categorie': 'Web',
            'tags': 'rest,api,web-services,http',
            'auteur': 'API Designer',
            'url': 'https://rest-api-guide.com',
            'date_publication': '2025-01-30'
        },
        {
            'titre': 'Cloud Computing with AWS',
            'description': 'Cloud computing fundamentals and AWS services',
            'contenu': 'Cloud computing is the on-demand availability of computer system resources through the Internet. AWS provides services like EC2, S3, Lambda that enable scalable and reliable computing infrastructure without managing physical hardware.',
            'categorie': 'Infrastructure',
            'tags': 'cloud,aws,devops,infrastructure',
            'auteur': 'Cloud Architect',
            'url': 'https://aws.amazon.com',
            'date_publication': '2025-02-03'
        },
        {
            'titre': 'Cybersecurity Essentials',
            'description': 'Protect systems and networks from attacks',
            'contenu': 'Cybersecurity is the practice of protecting systems, networks, and data from digital attacks. This includes secure coding, encryption, authentication, and security audits. Every developer should understand basic security principles.',
            'categorie': 'Security',
            'tags': 'security,cryptography,networks,protection',
            'auteur': 'Security Expert',
            'url': 'https://owasp.org',
            'date_publication': '2025-02-07'
        },
        {
            'titre': 'Docker Containerization',
            'description': 'Container technology for application deployment',
            'contenu': 'Docker is a containerization platform that packages applications and dependencies into isolated containers. Containers are lightweight, portable, and ensure consistency across different environments. Docker simplifies deployment and scaling.',
            'categorie': 'DevOps',
            'tags': 'docker,containers,devops,deployment',
            'auteur': 'DevOps Engineer',
            'url': 'https://docker.com',
            'date_publication': '2025-02-09'
        }
    ]
    
    print("\n" + "="*60)
    print("Insertion des données de test...")
    print("="*60 + "\n")
    
    inserted = 0
    for i, doc in enumerate(documents, 1):
        try:
            doc_id = DatabaseService.add_document(
                titre=doc['titre'],
                description=doc['description'],
                contenu=doc['contenu'],
                categorie=doc['categorie'],
                tags=doc['tags'],
                auteur=doc['auteur'],
                url=doc['url'],
                date_publication=doc['date_publication']
            )
            print(f"✓ [{i}/10] {doc['titre']:<40} (ID: {doc_id})")
            inserted += 1
        except Exception as e:
            print(f"✗ [{i}/10] {doc['titre']:<40} - Erreur: {str(e)[:50]}")
    
    print("\n" + "="*60)
    print(f"✅ {inserted}/10 documents insérés avec succès!")
    print("="*60 + "\n")
    
    # Vérifier les documents
    print("Documents en base de données:")
    print("-"*60)
    try:
        all_docs = DatabaseService.get_all_documents()
        print(f"Total: {len(all_docs)} documents\n")
        for doc in all_docs[:5]:
            print(f"  • [{doc.id}] {doc.titre} ({doc.categorie})")
        if len(all_docs) > 5:
            print(f"  ... et {len(all_docs) - 5} autres documents")
    except Exception as e:
        print(f"Erreur lors de la lecture: {e}")
    
    print("-"*60 + "\n")

if __name__ == '__main__':
    insert_test_data()
