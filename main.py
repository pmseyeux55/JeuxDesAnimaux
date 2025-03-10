import pygame
import sys
import subprocess
import traceback  # Pour le débogage
import os
import time
import signal
from game.game import Game
from game.animal import Animal
from game.resources import Fruit
from ui.gui import GUI
from ui.menu import MainMenu
from game.config import (
    LION_START_POSITION, TIGER_START_POSITION,
    GREEN_FRUIT_POSITIONS, RED_FRUIT_POSITIONS
)

# Variable globale pour le processus serveur
server_process = None

def cleanup():
    """Nettoie les ressources avant de quitter"""
    global server_process
    if server_process:
        print("Arrêt du serveur...")
        try:
            server_process.terminate()
            server_process.wait(timeout=2)
        except:
            if server_process.poll() is None:
                server_process.kill()
        print("Serveur arrêté")
    pygame.quit()

def main():
    global server_process
    
    # Initialiser pygame
    pygame.init()
    
    try:
        print("Démarrage du jeu...")
        # Afficher le menu principal
        menu = MainMenu()
        result = menu.run()
        
        print(f"Action sélectionnée: {result['action']}")
        
        # Traiter le résultat du menu
        if result["action"] == "quit":
            cleanup()
            sys.exit()
        
        elif result["action"] == "single_player":
            print("Démarrage du mode solo...")
            # Mode solo (comportement actuel)
            # Utiliser l'écran de configuration pour créer le jeu
            game = GUI.setup_game()
            
            # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
            if game is None:
                print("Configuration annulée")
                return
            
            print("Lancement de l'interface graphique en mode solo...")
            # Lancer l'interface graphique
            gui = GUI(game)
            gui.run()
        
        elif result["action"] == "host_game":
            print("Démarrage du mode hôte...")
            # Héberger une partie en mode serveur
            try:
                # Vérifier si le serveur est déjà en cours d'exécution
                import socket
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    test_socket.bind(("127.0.0.1", 5555))
                    test_socket.close()
                except OSError:
                    print("ERREUR: Le port 5555 est déjà utilisé. Un autre serveur est peut-être en cours d'exécution.")
                    return
                
                print("Lancement du serveur...")
                # Utiliser le chemin absolu pour le script server.py
                server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
                server_process = subprocess.Popen(
                    [sys.executable, server_script, "--host", "127.0.0.1"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                print(f"Serveur démarré avec PID: {server_process.pid}")
                
                # Attendre que le serveur démarre
                time.sleep(1)
                
                # Vérifier si le serveur est toujours en cours d'exécution
                if server_process.poll() is not None:
                    print(f"Le serveur s'est arrêté avec le code: {server_process.returncode}")
                    stdout, stderr = server_process.communicate()
                    print(f"Sortie standard du serveur: {stdout.decode('utf-8')}")
                    print(f"Erreur standard du serveur: {stderr.decode('utf-8')}")
                    return
                
                print("Serveur démarré, importation des modules...")
                # Importer le client réseau
                from network.client import GameClient
                from client import NetworkedGUI
                
                print("Connexion au serveur local...")
                # Se connecter au serveur local
                client = GameClient("127.0.0.1")
                
                # Essayer de se connecter plusieurs fois
                connected = False
                for attempt in range(3):
                    if client.connect():
                        connected = True
                        break
                    print(f"Tentative de connexion {attempt+1} échouée, nouvelle tentative...")
                    time.sleep(1)
                
                if connected:
                    print("Connecté au serveur, création de l'interface...")
                    # Créer une instance de Game vide
                    game_instance = Game()
                    print("Instance de jeu créée")
                    
                    # Créer une instance de NetworkedGUI
                    print("Création de l'interface réseau...")
                    gui = NetworkedGUI(game_instance, client)
                    print("Interface réseau créée")
                    
                    print("Configuration de l'animal...")
                    # Utiliser l'écran de configuration pour créer le jeu
                    # et passer le callback pour signaler que la configuration est terminée
                    game = GUI.setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
                    # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
                    if game is None:
                        print("Configuration annulée")
                        client.disconnect()
                        return
                    
                    print("Lancement de l'interface graphique...")
                    # Lancer l'interface graphique en mode réseau
                    gui.run()
                    
                    # Déconnecter le client
                    print("Déconnexion du client...")
                    client.disconnect()
                else:
                    print("Impossible de se connecter au serveur local après plusieurs tentatives")
            
            except Exception as e:
                print(f"Erreur en mode hôte: {e}")
                traceback.print_exc()  # Afficher la trace complète
        
        elif result["action"] == "join_game":
            print("Démarrage du mode client...")
            host = result.get("host", "127.0.0.1")
            
            try:
                print(f"Importation des modules pour se connecter à {host}...")
                # Importer le client réseau
                from network.client import GameClient
                from client import NetworkedGUI
                
                print(f"Connexion au serveur {host}...")
                # Se connecter au serveur
                client = GameClient(host)
                
                # Essayer de se connecter plusieurs fois
                connected = False
                for attempt in range(3):
                    if client.connect():
                        connected = True
                        break
                    print(f"Tentative de connexion {attempt+1} échouée, nouvelle tentative...")
                    time.sleep(1)
                
                if connected:
                    print("Connecté au serveur, création de l'interface...")
                    # Créer une instance de Game vide
                    game_instance = Game()
                    print("Instance de jeu créée")
                    
                    # Créer une instance de NetworkedGUI
                    print("Création de l'interface réseau...")
                    gui = NetworkedGUI(game_instance, client)
                    print("Interface réseau créée")
                    
                    print("Configuration de l'animal...")
                    # Utiliser l'écran de configuration pour créer le jeu
                    # et passer le callback pour signaler que la configuration est terminée
                    game = GUI.setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
                    # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
                    if game is None:
                        print("Configuration annulée")
                        client.disconnect()
                        return
                    
                    print("Lancement de l'interface graphique...")
                    # Lancer l'interface graphique en mode réseau
                    gui.run()
                    
                    # Déconnecter le client
                    print("Déconnexion du client...")
                    client.disconnect()
                else:
                    print(f"Impossible de se connecter au serveur {host} après plusieurs tentatives")
            
            except Exception as e:
                print(f"Erreur en mode client: {e}")
                traceback.print_exc()  # Afficher la trace complète
    
    except Exception as e:
        print(f"Erreur générale: {e}")
        traceback.print_exc()  # Afficher la trace complète
    
    # Nettoyer avant de quitter
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
    finally:
        cleanup() 