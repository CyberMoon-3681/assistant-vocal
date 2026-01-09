#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assistant Vocal Local "Spotify-Link"
Script Python pour contrôler Spotify via commandes vocales en local.
"""

import json
import subprocess
import os
import sys
import time
import keyboard
from typing import Optional

try:
    import vosk
    import pyaudio
    import pyttsx3
    import requests
except ImportError as e:
    print(f"❌ Module manquant : {e}")
    print("📦 Installez les dépendances avec : pip install -r requirements.txt")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# Chemin vers l'exécutable Spotify (à adapter selon votre installation)
SHORTCUTS_PATH = r"C:\Users\jaige\Desktop\ia_perso\IA_Test\shortcuts"
SPOTIFY_PATH = r"C:\Users\jaige\Desktop\ia_perso\IA_Test\shortcuts\Spotify_shortcut.lnk"

# Base de données des logiciels disponibles
SOFTWARE_DB = {}

# Chemin vers le modèle Vosk (sera téléchargé automatiquement si nécessaire)
VOSK_MODEL_PATH = r"vosk-model-small-fr-0.22"

# Configuration Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # Le nom du modèle (peut être mistral, mistral:latest, etc.)

# Variable globale pour stocker le nom exact du modèle trouvé
OLLAMA_MODEL_ACTUAL = None

# Configuration audio
SAMPLE_RATE = 16000
CHUNK_SIZE = 4000

# Seuil de longueur minimale du texte pour l'analyse
MIN_TEXT_LENGTH = 3


# ==================== FONCTIONS ====================

def load_software_db() -> None:
    """
    Charge la base de données des logiciels depuis le dossier shortcuts.
    """
    global SOFTWARE_DB
    if not os.path.exists(SHORTCUTS_PATH):
        print(f"⚠️  Dossier shortcuts introuvable : {SHORTCUTS_PATH}")
        return
    
    SOFTWARE_DB = {}
    for file in os.listdir(SHORTCUTS_PATH):
        if file.endswith('.lnk'):
            # Supposer que le nom est avant '_shortcut.lnk'
            name = file.replace('_shortcut.lnk', '').lower()
            path = os.path.join(SHORTCUTS_PATH, file)
            SOFTWARE_DB[name] = path
        elif file.endswith('.url'):
            name = file.replace('.url', '').lower()
            path = os.path.join(SHORTCUTS_PATH, file)
            SOFTWARE_DB[name] = path
    
    print(f"✅ Base de données logiciels chargée : {list(SOFTWARE_DB.keys())}")


def initialiser_voix() -> pyttsx3.Engine:
    """
    Configure et initialise le moteur de synthèse vocale pyttsx3.
    
    Returns:
        pyttsx3.Engine: Moteur TTS configuré
    """
    try:
        engine = pyttsx3.init()
        
        # Configuration de la voix française
        voices = engine.getProperty('voices')
        # Chercher une voix française si disponible
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Configuration de la vitesse (mots par minute)
        engine.setProperty('rate', 150)
        
        # Configuration du volume (0.0 à 1.0)
        engine.setProperty('volume', 5.0)
        
        print("✅ Voix initialisée")
        return engine
    
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la voix : {e}")
        sys.exit(1)


def parler(engine: pyttsx3.Engine, texte: str) -> None:
    """
    Fait parler l'assistant avec le texte fourni.
    
    Args:
        engine: Moteur TTS
        texte: Texte à prononcer
    """
    try:
        engine.say(texte)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ Erreur lors de la synthèse vocale : {e}")


def verifier_ollama() -> bool:
    """
    Vérifie si Ollama est accessible et si le modèle est disponible.
    
    Returns:
        bool: True si Ollama est accessible, False sinon
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            
            # Vérifier si le modèle existe (exact ou avec variante comme mistral:latest)
            model_found = False
            matching_model = None
            
            for model_name in model_names:
                # Vérifier correspondance exacte ou si le nom commence par le modèle (ex: mistral:latest)
                if model_name == OLLAMA_MODEL or model_name.startswith(OLLAMA_MODEL + ':'):
                    model_found = True
                    matching_model = model_name
                    break
            
            if model_found:
                global OLLAMA_MODEL_ACTUAL
                OLLAMA_MODEL_ACTUAL = matching_model
                print(f"✅ Ollama accessible avec le modèle '{matching_model}'")
                return True
            else:
                print(f"⚠️  Modèle '{OLLAMA_MODEL}' non trouvé. Modèles disponibles : {model_names}")
                print(f"💡 Installez le modèle avec : ollama pull {OLLAMA_MODEL}")
                return False
        return False
    except requests.exceptions.RequestException:
        print("❌ Ollama n'est pas accessible. Assurez-vous qu'Ollama est démarré.")
        return False


def analyser_intention_mots_cles(texte: str) -> Optional[str]:
    """
    Analyse rapide basée sur des mots-clés (fallback si Ollama est trop lent).
    
    Args:
        texte: Texte transcrit à analyser
        
    Returns:
        str: 'ACTION_SPOTIFY' si détecté, None sinon
    """
    if not texte:
        return None
    
    texte_lower = texte.lower()
    
    # Vérifier si le texte demande de lancer un logiciel disponible
    for name, path in SOFTWARE_DB.items():
        if f"lance {name}" in texte_lower or f"ouvre {name}" in texte_lower or f"démarre {name}" in texte_lower or f"start {name}" in texte_lower:
            return f'LAUNCH_SOFTWARE:{name}'
    
    # Mots-clés qui indiquent une intention de lancer Spotify (fallback)
    mots_cles_spotify = [
        'lance spotify', 'ouvre spotify', 'démarre spotify', 'start spotify',
        'lance spotify', 'ouvrir spotify', 'démarrer spotify',
        'spotify', 'ouvre spotify', 'lance spotify'
    ]

    mots_cles_play_pause = [
        'pause', 'arrête', 'reprends', 'stop',
        'stoppe', 'arrête la musique', 'pause la musique',
        'reprends la musique', 'stoppe la musique',
        'reprend', 'relance', 'relance la musique', 'relance la chanson',
    ]

    mots_cles_volume_up = [
        'plus fort', 'monte le son', 'augmente le son', 
        'augmente le volume', 'monte le volume'
    ]

    mots_cles_volume_down = [
        'moins fort', 'baisse le son', 'diminue le son', 
        'diminue le volume', 'baisse le volume'
    ]

    mots_cles_next = [
        'suivant', 'prochain', 'next', 'prochaine', 
        'suivante', 'passe'
    ]

    mots_cles_previous = [
        'précédent', 'précédente', 'previous', 'revient', 
        'reviens', 'return', 'retour', 'retourne'
    ]

    mots_cles_shuffle = [
        'shuffle', 'mélange', 'mélange la musique', 
        'mélange la chanson', 'aléatoire'
    ]

    mots_cles_repeat = [
        'repeat', 'répète', 'répète la chanson', 
        'répète la musique', 'répète'
    ]

    mots_cles_playlist = [
        'met la playlist', 'joue la playlist', 'playlist'
    ]


    # Vérifier si le texte contient des mots-clés Spotify
    for mot_cle in mots_cles_spotify:
        if mot_cle in texte_lower:
            return 'ACTION_SPOTIFY'
    for mot_cle in mots_cles_play_pause:
        if mot_cle in texte_lower:
            return 'PLAY_PAUSE'
    for mot_cle in mots_cles_volume_up:
        if mot_cle in texte_lower:
            return 'VOLUME_UP'
    for mot_cle in mots_cles_volume_down:
        if mot_cle in texte_lower:
            return 'VOLUME_DOWN'
    for mot_cle in mots_cles_next:
        if mot_cle in texte_lower:
            return 'NEXT_SONG'
    for mot_cle in mots_cles_previous:
        if mot_cle in texte_lower:
            return 'PREVIOUS_SONG'
    for mot_cle in mots_cles_shuffle:
        if mot_cle in texte_lower:
            return 'SHUFFLE'
    for mot_cle in mots_cles_repeat:
        if mot_cle in texte_lower:
            return 'REPEAT'
    for mot_cle in mots_cles_playlist:
        if mot_cle in texte_lower:
            return 'PLAYLIST'
    
    return None


def analyser_intention(texte: str) -> Optional[str]:
    """
    Analyse l'intention de l'utilisateur via Ollama (Mistral) avec fallback sur mots-clés.
    
    Args:
        texte: Texte transcrit à analyser
        
    Returns:
        str: 'ACTION_SPOTIFY' si l'utilisateur veut lancer Spotify, 'IGNORE' sinon, None en cas d'erreur
    """
    if not texte or len(texte.strip()) < MIN_TEXT_LENGTH:
        return None
    
    # D'abord, essayer la détection rapide par mots-clés
    intention_mots_cles = analyser_intention_mots_cles(texte)
    if intention_mots_cles:
        print("🔍 Intention détectée par mots-clés (rapide)")
        return intention_mots_cles
    
    # Si pas de mots-clés évidents, utiliser Ollama pour une analyse plus fine
    # Prompt optimisé pour une réponse rapide et concise
    prompt_system = (
        "Analyse: l'utilisateur veut-il lancer Spotify? "
        "Réponds UNIQUEMENT 'ACTION_SPOTIFY' ou 'IGNORE'."
    )
    
    prompt_complet = f"{prompt_system}\n\nTexte: {texte}\n\nRéponse:"
    
    try:
        # Utiliser le nom exact du modèle trouvé, ou le nom par défaut
        model_to_use = OLLAMA_MODEL_ACTUAL if OLLAMA_MODEL_ACTUAL else OLLAMA_MODEL
        
        payload = {
            "model": model_to_use,
            "prompt": prompt_complet,
            "stream": False,
            "options": {
                "temperature": 0.0,   # Température à 0 pour des réponses déterministes
                "num_predict": 3,     # Limite la réponse à très peu de tokens (ACTION_SPOTIFY ou IGNORE)
                "num_ctx": 64,        # Réduit le contexte pour accélérer
                "top_k": 1,           # Réduit les options de génération
                "top_p": 0.1          # Réduit la diversité
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        reponse_llm = result.get('response', '').strip().upper()
        
        # Nettoyer la réponse pour extraire ACTION_SPOTIFY ou IGNORE
        if 'ACTION_SPOTIFY' in reponse_llm:
            return 'ACTION_SPOTIFY'
        elif 'PLAY_PAUSE' in reponse_llm:
            return 'PLAY_PAUSE'
        elif 'NEXT_SONG' in reponse_llm:
            return 'NEXT_SONG'
        elif 'PREVIOUS_SONG' in reponse_llm:
            return 'PREVIOUS_SONG'
        elif 'VOLUME_UP' in reponse_llm:
            return 'VOLUME_UP'
        elif 'VOLUME_DOWN' in reponse_llm:
            return 'VOLUME_DOWN'
        elif 'SHUFFLE' in reponse_llm:
            return 'SHUFFLE'
        elif 'REPEAT' in reponse_llm:
            return 'REPEAT'
        elif 'PLAYLIST' in reponse_llm:
            return 'PLAYLIST'
        elif 'IGNORE' in reponse_llm:
            return 'IGNORE'
        else:
            # Si la réponse n'est pas claire, on ignore par défaut
            return 'IGNORE'
    
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout Ollama - Utilisation de la détection par mots-clés")
        # En cas de timeout, utiliser la détection par mots-clés
        intention_mots_cles = analyser_intention_mots_cles(texte)
        if intention_mots_cles:
            return intention_mots_cles
        return 'IGNORE'  # Par défaut, ignorer si pas de mots-clés
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête à Ollama : {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de l'intention : {e}")
        return None


def executer_action(code_intention: str, engine: pyttsx3.Engine, texte: str = "") -> None:
    """
    Exécute l'action correspondant au code d'intention.
    
    Args:
        code_intention: Code d'intention ('ACTION_SPOTIFY' ou 'IGNORE')
        engine: Moteur TTS pour les réponses vocales
    """
    if code_intention.startswith('LAUNCH_SOFTWARE:'):
        name = code_intention.split(':', 1)[1]
        if name in SOFTWARE_DB:
            lancer_logiciel(SOFTWARE_DB[name], name, engine)
        else:
            parler(engine, f"Logiciel {name} non trouvé")
    elif code_intention == 'ACTION_SPOTIFY':
        lancer_spotify(engine)
    elif code_intention == 'PLAY_PAUSE':
        play_pause(engine)
    elif code_intention == 'NEXT_SONG':
        next_song(engine)
    elif code_intention == 'PREVIOUS_SONG':
        previous_song(engine)
    elif code_intention == 'VOLUME_UP':
        volume_up(engine)
    elif code_intention == 'VOLUME_DOWN':
        volume_down(engine)
    elif code_intention == 'SHUFFLE':
        shuffle(engine)
    elif code_intention == 'REPEAT':
        repeat(engine)
    elif code_intention == 'PLAYLIST':
        playlist(engine)
    elif code_intention == 'IGNORE':
        # Ne rien faire, juste continuer à écouter
        pass


def ecouter_nom_playlist(engine: pyttsx3.Engine) -> str:
    """
    Écoute le microphone et retourne le nom de la playlist dicté par l'utilisateur.
    
    Args:
        engine: Moteur TTS pour les réponses vocales
    
    Returns:
        str: Nom de la playlist transcrit depuis le microphone
    """
    # Vérifier et télécharger le modèle Vosk
    model_path = telecharger_modele_vosk()
    if not model_path:
        print("❌ Modèle Vosk introuvable. Veuillez le télécharger.")
        parler(engine, "Modèle de reconnaissance vocale introuvable")
        return ""
    
    try:
        # Charger le modèle Vosk
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        recognizer.SetWords(True)
        
        # Initialiser PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("🎤 Parlez maintenant le nom de la playlist...")
        
        nom_playlist = ""
        timeout_counter = 0
        max_timeout = 150  # Nombre d'itérations avant timeout (environ 15 secondes)
        
        while True:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                timeout_counter += 1
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    texte = result.get('text', '').strip()
                    
                    if texte:
                        nom_playlist = texte
                        print(f"🎤 Nom de la playlist capté : {nom_playlist}")
                        break
                
                # Si on n'a rien capté après un certain temps, vérifier les résultats partiels
                if timeout_counter > max_timeout and not nom_playlist:
                    # Essayer de récupérer le dernier résultat partiel
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    if partial_text and len(partial_text) > 2:
                        nom_playlist = partial_text
                        print(f"🎤 Nom de la playlist capté (partiel) : {nom_playlist}")
                        break
                
                if timeout_counter > max_timeout * 2:
                    print("⏱️  Timeout : aucune réponse détectée")
                    parler(engine, "Je n'ai rien entendu. Veuillez réessayer.")
                    break
            
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                print(f"❌ Erreur lors de l'écoute : {e}")
                continue
        
        # Nettoyage
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        return nom_playlist.strip()
    
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du microphone : {e}")
        parler(engine, "Erreur lors de l'initialisation du microphone")
        return ""

def lancer_logiciel(path: str, name: str, engine: pyttsx3.Engine) -> None:
    """
    Lance un logiciel via son raccourci.
    
    Args:
        path: Chemin vers le raccourci .lnk
        name: Nom du logiciel
        engine: Moteur TTS pour les réponses vocales
    """
    try:
        if not os.path.exists(path):
            print(f"❌ Raccourci introuvable : {path}")
            parler(engine, f"Raccourci pour {name} introuvable")
            return
        
        # Essayer de lancer via subprocess
        subprocess.Popen([path], shell=True)
        print(f"✅ {name} lancé")
        parler(engine, f"{name} lancé")
    
    except Exception as e:
        print(f"❌ Erreur lors du lancement de {name} : {e}")
        parler(engine, f"Impossible de lancer {name}")


def lancer_spotify(engine: pyttsx3.Engine) -> None:
    """
    Lance l'application Spotify.
    
    Args:
        engine: Moteur TTS pour les réponses vocales
    """
    try:
        # Vérifier si Spotify est déjà en cours d'exécution
        # Sur Windows, on peut vérifier avec tasklist
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq Spotify.exe'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'Spotify.exe' in result.stdout:
            print("ℹ️  Spotify est déjà en cours d'exécution")
            parler(engine, "Spotify est déjà lancé")
            return
        
        # Méthode 1 : Essayer avec le protocole URI spotify: (méthode la plus fiable)
        try:
            subprocess.Popen(['start', 'spotify:'], shell=True)
            print("✅ Spotify lancé via protocole URI")
            parler(engine, "Spotify lancé")
            return
        except:
            pass
        
        # Méthode 2 : Essayer avec le chemin direct si accessible
        if os.path.exists(SPOTIFY_PATH):
            try:
                # Utiliser shell=True pour contourner les restrictions de WindowsApps
                subprocess.Popen([SPOTIFY_PATH], shell=True)
                print("✅ Spotify lancé via chemin direct")
                parler(engine, "Spotify lancé")
                return
            except Exception as e:
                print(f"⚠️  Méthode chemin direct échouée : {e}")
        
        # Méthode 3 : Essayer avec PowerShell pour lancer depuis WindowsApps
        try:
            ps_command = f'Start-Process "{SPOTIFY_PATH}"'
            subprocess.run(
                ['powershell', '-Command', ps_command],
                timeout=10,
                capture_output=True
            )
            print("✅ Spotify lancé via PowerShell")
            parler(engine, "Spotify lancé")
            return
        except Exception as e:
            print(f"⚠️  Méthode PowerShell échouée : {e}")
        
        # Méthode 4 : Essayer simplement "spotify" comme commande
        try:
            subprocess.Popen(['spotify'], shell=True)
            print("✅ Spotify lancé via commande simple")
            parler(engine, "Spotify lancé")
            return
        except:
            pass
        
        # Si toutes les méthodes échouent
        print("❌ Impossible de lancer Spotify avec les méthodes disponibles")
        parler(engine, "Impossible de lancer Spotify. Essayez de l'ouvrir manuellement.")
    
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout lors de la vérification de Spotify")
        parler(engine, "Erreur lors du lancement de Spotify")
    except Exception as e:
        print(f"❌ Erreur lors du lancement de Spotify : {e}")
        parler(engine, "Erreur lors du lancement de Spotify")

def play_pause(engine):
    keyboard.send('space')
    parler(engine, "Play ou pause")

def next_song(engine):
    keyboard.send('ctrl+right')
    parler(engine, "musique suivante")

def previous_song(engine):
    keyboard.send('ctrl+left')
    parler(engine, "musique précédente")

def volume_up(engine):
    keyboard.send('ctrl+up')
    parler(engine, "volume monté")

def volume_down(engine):
    keyboard.send('ctrl+down')
    parler(engine, "volume baissé")

def shuffle(engine):
    keyboard.send('ctrl+s')
    parler(engine, "aléatoire activé")

def repeat(engine):
    keyboard.send('ctrl+r')
    parler(engine, "répétition activé")

def playlist(engine, nom_playlist=None):
    """
    Ouvre la recherche Spotify et recherche la playlist spécifiée.
    
    Args:
        engine: Moteur TTS pour les réponses vocales
        nom_playlist: Nom de la playlist (optionnel, sera demandé via micro si None)
    """
    # Si le nom de la playlist n'est pas fourni, l'écouter via le microphone
    if not nom_playlist:
        parler(engine, "Quelle playlist souhaitez-vous jouer ?")
        nom_playlist = ecouter_nom_playlist(engine)
    
    # Vérifier qu'on a bien un nom de playlist
    if not nom_playlist or not nom_playlist.strip():
        parler(engine, "Désolé, je n'ai pas pu entendre le nom de la playlist.")
        return
    
    # Ouvrir la recherche Spotify et saisir le nom de la playlist
    keyboard.send('ctrl+k')
    # Petite pause pour s'assurer que la recherche est ouverte
    time.sleep(0.3)
    keyboard.write(nom_playlist)
    time.sleep(0.2)
    keyboard.send('shift+enter')
    time.sleep(0.2)
    parler(engine, f"Playlist {nom_playlist} activée")
    keyboard.send('escape')

def telecharger_modele_vosk() -> Optional[str]:
    """
    Télécharge le modèle Vosk si nécessaire.
    
    Returns:
        str: Chemin vers le modèle, None si erreur
    """
    if os.path.exists(VOSK_MODEL_PATH) and os.path.isdir(VOSK_MODEL_PATH):
        print(f"✅ Modèle Vosk trouvé : {VOSK_MODEL_PATH}")
        return VOSK_MODEL_PATH
    
    print(f"📥 Téléchargement du modèle Vosk...")
    print(f"💡 Téléchargez manuellement depuis : https://alphacephei.com/vosk/models")
    print(f"💡 Ou utilisez : python -m vosk --model vosk-model-small-fr-0.22")
    return None


def ecouter_micro(engine: pyttsx3.Engine) -> None:
    """
    Écoute le microphone en continu et traite les commandes vocales.
    
    Args:
        engine: Moteur TTS
    """
    # Vérifier et télécharger le modèle Vosk
    model_path = telecharger_modele_vosk()
    if not model_path:
        print("❌ Modèle Vosk introuvable. Veuillez le télécharger.")
        parler(engine, "Modèle de reconnaissance vocale introuvable")
        return
    
    try:
        # Charger le modèle Vosk
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        recognizer.SetWords(True)
        
        # Initialiser PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        logiciels_disponibles = ', '.join(SOFTWARE_DB.keys()) if SOFTWARE_DB else 'aucun'
        print(f"🎤 Microphone activé. Logiciels disponibles : {logiciels_disponibles}. Dites 'lance [nom]' pour démarrer.")
        print("💬 Appuyez sur Ctrl+C pour arrêter.\n")
        
        buffer_texte = ""
        dernier_texte = ""
        
        while True:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    texte = result.get('text', '').strip()
                    
                    if texte and texte != dernier_texte:
                        print(f"🎤 Vous avez dit : {texte}")
                        buffer_texte = texte
                        dernier_texte = texte
                        
                        # Analyser l'intention
                        intention = analyser_intention(buffer_texte)
                        
                        if intention:
                            print(f"🧠 Intention détectée : {intention}")
                            executer_action(intention, engine)
                            buffer_texte = ""  # Réinitialiser le buffer
                
                else:
                    # Résultat partiel (en cours de reconnaissance)
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    if partial_text:
                        # Afficher le texte partiel (optionnel, peut être commenté)
                        pass
            
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                print(f"❌ Erreur lors de l'écoute : {e}")
                continue
        
        # Nettoyage
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("✅ Microphone fermé")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du microphone : {e}")
        parler(engine, "Erreur lors de l'initialisation du microphone")


def main_loop() -> None:
    """
    Boucle principale qui orchestre toutes les fonctionnalités.
    """
    print("=" * 60)
    print("🎵 Assistant Vocal Local 'Spotify-Link'")
    print("=" * 60)
    print()
    
    # Initialiser la voix
    engine = initialiser_voix()
    
    # Charger la base de données des logiciels
    load_software_db()
    
    # Vérifier Ollama
    if not verifier_ollama():
        print("\n⚠️  Ollama n'est pas correctement configuré. Le script continuera mais l'analyse d'intention ne fonctionnera pas.")
        print("   Assurez-vous qu'Ollama est démarré et que le modèle 'mistral' est installé.")
        reponse = input("Voulez-vous continuer quand même ? (o/n) : ")
        if reponse.lower() != 'o':
            sys.exit(1)
    
    # Message de bienvenue vocal
    logiciels_disponibles = ', '.join(SOFTWARE_DB.keys()) if SOFTWARE_DB else 'aucun'
    parler(engine, f"Assistant vocal initialisé. Logiciels disponibles : {logiciels_disponibles}. Dites 'lance [nom]' pour démarrer un logiciel.")
    
    # Démarrer l'écoute
    ecouter_micro(engine)
    
    # Message de fin
    parler(engine, "Au revoir")
    print("\n👋 Au revoir !")


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du programme")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        sys.exit(1)

