# 🎵 Assistant Vocal Local "Spotify-Link"

Assistant vocal fonctionnant à 100% en local (hors-ligne) capable d'écouter l'utilisateur, d'interpréter son intention via un LLM local (Ollama), de lancer divers logiciel, de contrôler spotify et de répondre vocalement.

## 📋 Fonctionnalités

- **Reconnaissance vocale** : Utilise Vosk avec le modèle français léger
- **Analyse d'intention** : Utilise Ollama avec le modèle Mistral pour comprendre les commandes
- **Lancement de Spotify** : Lance automatiquement Spotify sur Windows
- **Réponses vocales** : Utilise pyttsx3 pour répondre vocalement

## 🛠️ Prérequis

1. **Python 3.10+** installé
2. **Ollama** installé et démarré
3. **Modèle Mistral** installé dans Ollama
4. **Spotify** installé sur votre système

## 📦 Installation

### 1. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Installer Ollama

Téléchargez et installez Ollama depuis : https://ollama.ai/

### 3. Installer le modèle Mistral dans Ollama

```bash
ollama pull mistral
```

### 4. Télécharger le modèle Vosk

Le modèle Vosk sera téléchargé automatiquement lors de la première exécution, ou vous pouvez le télécharger manuellement :

```bash
# Option 1 : Téléchargement automatique (si disponible)
python -m vosk --model vosk-model-small-fr-0.22

# Option 2 : Téléchargement manuel
# Téléchargez depuis : https://alphacephei.com/vosk/models
# Extrayez dans le dossier du projet
```

### 5. Configurer le chemin des divers logiciels

Faites un copié-coller des raccourcis des logiciel que vous souhaitez pouvoir ouvrir avec l'assistant dans le dossier shortcuts.

Pour trouver le chemin de Spotify sur Windows :
- Ouvrez le Gestionnaire des tâches (Ctrl+Shift+Échap)
- Onglet "Détails"
- Trouvez "Spotify.exe"
- Clic droit → "Ouvrir l'emplacement du fichier"

## 🚀 Utilisation

1. **Démarrer Ollama** (si ce n'est pas déjà fait) :
   ```bash
   ollama serve
   ```

2. **Lancer l'assistant** :
   ```bash
   python assistant_spotify.py
   ```

3. **Parler à l'assistant** :
   - Dites "lance (le nom du logiciel)" ou "ouvre (le nom du logiciel)" pour lancer l'application
   - L'assistant répondra vocalement
   - Appuyez sur `Ctrl+C` pour arrêter

## 🎯 Exemples de commandes vocales

- "Lance (nom logiciel)"
- "Ouvre (nom logiciel)"
- "Démarre (nom logiciel)"
- "Start (nom logiciel)"

Pour spotify :
- "monte le son"      permet de monter le son de spotify
- "baisse le son"     permet de baisser le son de spotify
- "pause"             permet de metre en pause votre musique
- "reprend"           permet de relancer votre musique
- "suivant"           permet de passer à la musique suivante
- "précédent"         permet de revenir à la musique précédente
- "mélange"           permet de changer le mode de lecture aléatoire
- "répète"            permet de changer le mode de répétition
- "met la playlist" puis attandez que l'assistant vous demmande quelle playlist puis "(nom playlist)"

## 🔧 Configuration avancée

### Modifier le modèle Ollama

Dans `assistant_spotify.py`, modifiez :
```python
OLLAMA_MODEL = "mistral"  # Changez pour un autre modèle
```

### Modifier la vitesse de la voix

Dans la fonction `initialiser_voix()`, modifiez :
```python
engine.setProperty('rate', 150)  # Ajustez la vitesse (mots par minute)
```

### Modifier le seuil de longueur minimale

```python
MIN_TEXT_LENGTH = 3  # Texte minimum pour l'analyse
```

## ⚠️ Dépannage

### Erreur : "Module manquant"
```bash
pip install -r requirements.txt
```

### Erreur : "Ollama n'est pas accessible"
- Vérifiez qu'Ollama est démarré : `ollama serve`
- Vérifiez que le modèle est installé : `ollama list`

### Erreur : "Modèle Vosk introuvable"
- Téléchargez le modèle depuis : https://alphacephei.com/vosk/models
- Extrayez-le dans le dossier du projet

### Erreur : "PyAudio installation failed"
Sur Windows, installez d'abord les dépendances système :
```bash
pip install pipwin
pipwin install pyaudio
```

Ou utilisez un wheel précompilé :
```bash
pip install pipwin
pipwin install pyaudio
```

### Spotify ne se lance pas
- Vérifiez que le chemin `SPOTIFY_PATH` est correct
- Vérifiez que Spotify est installé
- Essayez de lancer Spotify manuellement pour vérifier

## 📝 Structure du code

- `load_software_db()` : Charge la base de données des logiciels depuis le dossier shortcuts
- `initialiser_voix()` : Configure pyttsx3
- `ecouter_micro()` : Utilise Vosk pour la reconnaissance vocale
- `analyser_intention(texte)` : Envoie une requête à Ollama
- `executer_action(code_intention)` : Lance Spotify si nécessaire
- `main_loop()` : Orchestre toutes les fonctionnalités

## 📄 Licence

Ce projet est fourni tel quel, sans garantie.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.


