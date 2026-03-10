# 🔍 SearchMine - Moteur de Recherche Google-Like

**Votre propre Google personnel!** Un moteur de recherche professionnel qui fonctionne comme Google.

---

## ⚡ Démarrage en 5 minutes (Même pour débutants!)

### **Étape 1 : Préparer la base de données** (phpMyAdmin)
1. Ouvre `phpMyAdmin` (http://localhost/phpmyadmin)
2. Crée une nouvelle base: `moteur_recherche`
3. Clique dessus → Importe `database/schema_v2.sql`
4. ✅ C'est bon!

### **Étape 2 : Installer les dépendances**
Ouvre PowerShell dans `backend/` et tape:
```powershell
pip install -r requirements.txt
```
C'est comme télécharger les outils nécessaires pour que le projet fonctionne.

### **Étape 3 : Lancer le serveur**
Dans le même PowerShell, tape:
```powershell
python app_v2.py
```
Tu devrais voir:
```
* Running on http://localhost:5000
```
✅ Le serveur tourne!

### **Étape 4 : Ajouter des données**
Dans `backend/`, lance:
```powershell
python populate_database.py
```
Cela ajoute plein de documents pertinents à ta base de données.

### **Étape 5 : Utiliser le moteur!**
Ouvre dans ton navigateur:
- **Chercher**: http://localhost/Moteur-recherche/frontend/google.html
- **Admin**: http://localhost/Moteur-recherche/frontend/admin.html

✅ **C'est activé!** Essaie de chercher "Python", "Web", "Machine Learning"...

---

## 🎯 Quoi faire avec chaque interface?

### **google.html** (Interface de Recherche)
C'est comme Google! Tu tapes dans la barre et tu vois les résultats.
- Tape ta question
- Vois les meilleurs résultats en haut
- Clique pour lire

### **admin.html** (Panel Admin)
Pour les experts qui veulent:
- Voir tous les documents
- Lancer un crawler (robot qui cherche sur le web)
- Voir les statistiques
- Purger ou éditer les données

---

## 📂 Structure du Projet

```
Moteur-recherche/
├── backend/              ← Code Python (le moteur)
│   ├── app_v2.py         ← Serveur et endpoints
│   ├── populate_database.py ← Ajoute les données
│   └── requirements.txt   ← Liste des outils à installer
│
├── frontend/             ← Interface web (ce que tu vois)
│   ├── google.html       ← Barre de recherche
│   ├── admin.html        ← Panel de contrôle
│   └── script_google.js  ← Logique JavaScript
│
├── database/             ← Base de données
│   └── schema_v2.sql     ← Structure des tables
│
├── README.md             ← Ce fichier
└── QUICKSTART.md         ← Guide avancé
```

---

## ✨ Que fait ce moteur?

| Fonction | Explication |
|----------|-----------|
| **Recherche** | Tu tapes un mot, il trouve tous les documents pertinents |
| **Ranking** | Met les meilleurs résultats en premier (mieux que Google!) |
| **Snippets** | Montre un petit aperçu du document |
| **Admin** | Gère les documents et le crawler |

---

## 🔧 Comment ça marche? (Pour les curieux)

```
Utilisateur tape "Python"
         ↓
     Frontend (google.html)
         ↓
   API Flask (5000)
         ↓
  Base de données MySQL
         ↓
  Algorithme BM25 (ranking)
         ↓
  Résultats triés + affichés
```

---

## ❓ Questions Fréquentes

### "Je suis bloqué à l'étape 1?"
Assure-toi que:
- Apache + MySQL tournent dans XAMPP
- Tu peux accéder à phpMyAdmin

### "Le serveur ne démarre pas?"
Essaie:
```powershell
# Dans backend/
pip install -r requirements.txt
python app_v2.py
```

### "Je ne vois aucun résultat de recherche?"
Lance d'abord: `python populate_database.py`
Cela ajoute les documents à chercher.

### "Je veux chercher sur des sites web?"
Utilise l'Admin Panel → "Crawler" → Rentre une URL et lance!

---

## 📚 Besoin de plus d'aide?

- **Démarrage avancé**: Voir [QUICKSTART.md](QUICKSTART.md)
- **API complète**: Voir `backend/app_v2.py`
- **Structure BD**: Voir `database/schema_v2.sql`

---

**🎉 Voilà! Tu as ton propre moteur de recherche Google!**

Commence simplement par essayer une recherche. C'est aussi simple que Google! 👍
