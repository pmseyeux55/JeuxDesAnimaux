#!/usr/bin/env python3
"""
Script pour lancer un serveur de jeu des animaux.
"""
import sys
import argparse
import traceback
import socket
import time
from network.server import GameServer

def main():
    """Fonction principale"""
    try:
        print("Démarrage du serveur de jeu...")
        # Analyser les arguments de la ligne de commande
        parser = argparse.ArgumentParser(description="Serveur de jeu des animaux")
        parser.add_argument("--host", default="127.0.0.1", help="Adresse IP du serveur (par défaut: 127.0.0.1)")
        parser.add_argument("--port", type=int, default=5555, help="Port d'écoute du serveur (par défaut: 5555)")
        args = parser.parse_args()
        
        print(f"Configuration du serveur sur {args.host}:{args.port}")
        
        # Vérifier si le port est déjà utilisé
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind((args.host, args.port))
            test_socket.close()
            print(f"Le port {args.port} est disponible")
        except OSError as e:
            print(f"ERREUR: Le port {args.port} est déjà utilisé ou inaccessible: {e}")
            print("Essayez un autre port avec l'option --port")
            sys.exit(1)
        
        # Créer et démarrer le serveur
        server = GameServer(args.host, args.port)
        if not server.start():
            print("Impossible de démarrer le serveur")
            sys.exit(1)
        
        print(f"Serveur démarré sur {args.host}:{args.port}")
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        try:
            # Garder le serveur en cours d'exécution
            while True:
                time.sleep(1)  # Utiliser sleep au lieu de input() pour éviter de bloquer
        except KeyboardInterrupt:
            # Arrêter le serveur proprement
            print("Arrêt du serveur demandé par l'utilisateur")
            server.stop()
            print("Serveur arrêté")
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 