#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour télécharger automatiquement le modèle Vosk français
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path

# Configurer l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
MODEL_NAME = "vosk-model-small-fr-0.22"
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
MODEL_DIR = Path(MODEL_NAME)

def telecharger_fichier(url: str, destination: str) -> bool:
    """
    Télécharge un fichier depuis une URL.
    
    Args:
        url: URL du fichier à télécharger
        destination: Chemin de destination
        
    Returns:
        bool: True si le téléchargement a réussi, False sinon
    """
    try:
        print(f"📥 Téléchargement depuis : {url}")
        print(f"💾 Destination : {destination}")
        
        def progress_hook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            bar_length = 40
            filled = int(bar_length * count * block_size / total_size)
            bar = '█' * filled + '░' * (bar_length - filled)
            sys.stdout.write(f'\r[{bar}] {percent}%')
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n✅ Téléchargement terminé")
        return True
    
    except Exception as e:
        print(f"\n❌ Erreur lors du téléchargement : {e}")
        return False

def extraire_zip(zip_path: str, extract_to: Path) -> bool:
    """
    Extrait un fichier ZIP.
    
    Args:
        zip_path: Chemin vers le fichier ZIP
        extract_to: Dossier de destination
        
    Returns:
        bool: True si l'extraction a réussi, False sinon
    """
    try:
        print(f"\n📦 Extraction de {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to.parent)
        print("✅ Extraction terminée")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("📥 Téléchargement du modèle Vosk français")
    print("=" * 60)
    print()
    
    # Vérifier si le modèle existe déjà
    if MODEL_DIR.exists() and MODEL_DIR.is_dir():
        print(f"✅ Le modèle '{MODEL_NAME}' existe déjà dans : {MODEL_DIR.absolute()}")
        reponse = input("Voulez-vous le télécharger à nouveau ? (o/n) : ")
        if reponse.lower() != 'o':
            print("Téléchargement annulé.")
            return
    
    # Nom du fichier ZIP
    zip_file = f"{MODEL_NAME}.zip"
    
    # Télécharger le modèle
    if not telecharger_fichier(MODEL_URL, zip_file):
        print("\n❌ Échec du téléchargement.")
        print("\n💡 Vous pouvez télécharger manuellement depuis :")
        print(f"   {MODEL_URL}")
        print(f"\n   Puis extrayez '{zip_file}' dans le dossier du projet.")
        return
    
    # Extraire le modèle
    if not extraire_zip(zip_file, MODEL_DIR):
        print("\n❌ Échec de l'extraction.")
        return
    
    # Supprimer le fichier ZIP
    try:
        os.remove(zip_file)
        print(f"🗑️  Fichier temporaire '{zip_file}' supprimé")
    except:
        pass
    
    # Vérifier que le modèle est bien extrait
    if MODEL_DIR.exists() and MODEL_DIR.is_dir():
        print(f"\n✅ Modèle installé avec succès dans : {MODEL_DIR.absolute()}")
        print("\n🎉 Vous pouvez maintenant lancer l'assistant vocal !")
    else:
        print(f"\n⚠️  Le modèle devrait être dans : {MODEL_DIR.absolute()}")
        print("   Vérifiez manuellement que l'extraction a fonctionné.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Téléchargement interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        sys.exit(1)

