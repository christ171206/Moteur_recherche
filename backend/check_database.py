#!/usr/bin/env python3
"""
Script pour vérifier le contenu de la base de données
"""

import mysql.connector
from mysql.connector import Error

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'moteur_recherche'
}

def check_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Compter les documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"📊 Nombre total de documents: {count}")

        # Afficher quelques documents
        cursor.execute("SELECT id, titre, categorie FROM documents LIMIT 5")
        documents = cursor.fetchall()

        print("\n📋 Échantillon de documents:")
        for doc in documents:
            print(f"ID: {doc[0]} - {doc[1]} ({doc[2]})")

        # Tester une recherche
        cursor.execute("SELECT COUNT(*) FROM documents WHERE MATCH(titre, contenu) AGAINST('python' IN NATURAL LANGUAGE MODE)")
        python_count = cursor.fetchone()[0]
        print(f"\n🔍 Documents contenant 'python': {python_count}")

    except Error as e:
        print(f"❌ Erreur de connexion: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_database()