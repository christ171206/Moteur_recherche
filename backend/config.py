import os
from dotenv import load_dotenv

load_dotenv()

# Configuration MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Xampp par défaut sans mot de passe
    'database': 'moteur_recherche',
    'raise_on_warnings': True
}

# Configuration Flask
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000
