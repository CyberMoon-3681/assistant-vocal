#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour trouver Ollama sur Windows
"""

import os
import subprocess
import sys
from pathlib import Path

# Configurer l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def trouver_ollama():
    """Trouve le chemin d'Ollama sur Windows"""
    
    print("Recherche d'Ollama sur votre systeme...\n")
    
    # Chemins possibles où Ollama peut être installé
    chemins_possibles = [
        Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
        Path("C:/Program Files/Ollama/ollama.exe"),
        Path("C:/Program Files (x86)/Ollama/ollama.exe"),
    ]
    
    # Vérifier aussi dans le PATH
    try:
        result = subprocess.run(
            ["where", "ollama"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            chemins_possibles.insert(0, Path(result.stdout.strip().split('\n')[0]))
    except:
        pass
    
    # Chercher dans les chemins possibles
    for chemin in chemins_possibles:
        if chemin.exists():
            print(f"[OK] Ollama trouve : {chemin}")
            print(f"   Chemin absolu : {chemin.absolute()}")
            return str(chemin.absolute())
    
    print("[ERREUR] Ollama non trouve dans les emplacements standards.")
    print("\nEmplacements verifies :")
    for chemin in chemins_possibles:
        print(f"   - {chemin}")
    
    return None

def verifier_ollama_demarre(chemin_ollama=None):
    """Verifie si Ollama est en cours d'execution"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("\n[OK] Ollama est deja en cours d'execution !")
            return True
    except:
        pass
    
    print("\n[ATTENTION] Ollama n'est pas en cours d'execution.")
    if chemin_ollama:
        print(f"\nPour demarrer Ollama, executez :")
        print(f'   "{chemin_ollama}" serve')
        print(f"\n   Ou ajoutez Ollama au PATH et utilisez :")
        print(f"   ollama serve")
    else:
        print("\nDemarrez Ollama depuis le menu Demarrer ou en tant que service.")
    
    return False

def ajouter_au_path(chemin_ollama):
    """Donne des instructions pour ajouter Ollama au PATH"""
    dossier_ollama = Path(chemin_ollama).parent
    
    print("\n" + "="*60)
    print("Instructions pour ajouter Ollama au PATH :")
    print("="*60)
    print(f"\n1. Copiez ce chemin : {dossier_ollama}")
    print("\n2. Ouvrez les Variables d'environnement :")
    print("   - Appuyez sur Win + R")
    print("   - Tapez : sysdm.cpl")
    print("   - Onglet 'Avance' -> 'Variables d'environnement'")
    print("\n3. Dans 'Variables systeme', trouvez 'Path' et cliquez sur 'Modifier'")
    print("4. Cliquez sur 'Nouveau' et collez le chemin ci-dessus")
    print("5. Cliquez sur 'OK' sur toutes les fenetres")
    print("\n6. Redemarrez PowerShell/Terminal pour que les changements prennent effet")
    print("\n" + "="*60)

def main():
    chemin_ollama = trouver_ollama()
    
    if chemin_ollama:
        verifier_ollama_demarre(chemin_ollama)
        ajouter_au_path(chemin_ollama)
        
        print("\n" + "="*60)
        print("Solution temporaire (sans modifier le PATH) :")
        print("="*60)
        print(f'\nUtilisez le chemin complet : "{chemin_ollama}" pull mistral')
        print(f'\nOu pour demarrer : "{chemin_ollama}" serve')
    else:
        print("\nOllama n'est peut-etre pas installe correctement.")
        print("   Telechargez-le depuis : https://ollama.ai/")
        print("   Assurez-vous de l'installer avec les options par defaut.")

if __name__ == "__main__":
    main()

