import pygame
import sys
import subprocess
import traceback  # Pour le débogage
import os
import time
import signal
import socket
from game.game import Game
from game.animal import Animal
from game.resources import Fruit
from ui.gui import GUI
from ui.menu import MainMenu
from ui.lobby import Lobby  # Importer la classe Lobby
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
        
        # Boucle principale du jeu
        running = True
        while running:
            # Afficher le menu principal
            menu = MainMenu()
            result = menu.run()
            
            print(f"Action sélectionnée: {result['action']}")
            
            # Traiter le résultat du menu
            if result["action"] == "quit":
                running = False
                continue
            
            elif result["action"] == "single_player":
                print("Démarrage du mode solo...")
                # Mode solo (comportement actuel)
                # Utiliser l'écran de configuration pour créer le jeu
                game = GUI.setup_game()
                
                # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
                if game is None:
                    print("Configuration annulée")
                    continue
                
                print("Lancement de l'interface graphique en mode solo...")
                # Lancer l'interface graphique
                gui = GUI(game)
                gui.run()
            
            elif result["action"] == "host_game":
                # Boucle pour le mode multijoueur
                while True:
                    # Gérer le mode hôte
                    result = handle_host_game()
                    
                    # Si l'utilisateur veut quitter ou revenir au menu principal
                    if result["action"] == "quit":
                        running = False
                        break
                    elif result["action"] == "main_menu":
                        break
                    # Sinon, on reste dans la boucle multijoueur
            
            elif result["action"] == "join_game":
                host = result.get("host", "127.0.0.1")
                print(f"Tentative de connexion à l'hôte: {host}")
                
                # Vérifier si l'adresse IP est valide
                if host == "localhost" or host == "127.0.0.1" or len(host.strip()) == 0:
                    print("Utilisation de l'adresse localhost")
                    host = "127.0.0.1"
                
                # Boucle pour le mode multijoueur
                while True:
                    # Gérer le mode client
                    result = handle_join_game(host)
                    
                    # Si l'utilisateur veut quitter ou revenir au menu principal
                    if result["action"] == "quit":
                        running = False
                        break
                    elif result["action"] == "main_menu":
                        break
                    # Sinon, on reste dans la boucle multijoueur
    
    except Exception as e:
        print(f"Erreur générale: {e}")
        traceback.print_exc()  # Afficher la trace complète
    
    # Nettoyer avant de quitter
    cleanup()

def handle_host_game():
    """Gère le mode hôte du jeu
    
    Returns:
        dict: Résultat de l'action (quit, main_menu, etc.)
    """
    global server_process
    
    print("Démarrage du mode hôte...")
    
    # Obtenir l'adresse IP locale
    local_ip = get_local_ip()
    print(f"Adresse IP locale: {local_ip}")
    
    # Afficher des instructions pour les autres joueurs
    print("\n=== INSTRUCTIONS POUR LES AUTRES JOUEURS ===")
    print(f"Les autres joueurs doivent utiliser l'adresse IP suivante pour se connecter:")
    print(f"- Si sur le même réseau local: {local_ip}")
    print("- Si sur un réseau différent: Votre adresse IP publique (visitez https://www.whatismyip.com/)")
    print("Assurez-vous que le port 5555 est ouvert dans votre pare-feu et redirigé dans votre routeur si nécessaire.")
    print("===========================================\n")
    
    # Héberger une partie en mode serveur
    try:
        # Vérifier si le serveur est déjà en cours d'exécution
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            test_socket.bind(("0.0.0.0", 5555))
            test_socket.close()
        except OSError:
            print("ERREUR: Le port 5555 est déjà utilisé. Un autre serveur est peut-être en cours d'exécution.")
            return {"action": "main_menu"}
        
        print("Lancement du serveur...")
        # Utiliser le chemin absolu pour le script server.py
        server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
        server_process = subprocess.Popen(
            [sys.executable, server_script, "--host", "0.0.0.0"], 
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
            return {"action": "main_menu"}
        
        print("Serveur démarré, importation des modules...")
        # Importer le client réseau
        from network.client import GameClient
        from client import NetworkedGUI
        
        print("Connexion au serveur local...")
        # Se connecter au serveur local
        client = GameClient("127.0.0.1")  # Toujours utiliser 127.0.0.1 pour se connecter au serveur local
        
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
            
            # Créer une surface pygame pour le lobby
            screen = pygame.display.set_mode((900, 600))
            pygame.display.set_caption("Jeu des Animaux - Lobby")
            
            # Créer et exécuter le lobby
            print("Affichage du lobby...")
            lobby = Lobby(screen, local_ip, is_host=True, client=client)  # Utiliser l'adresse IP locale réelle
            lobby_result = lobby.run()
            print(f"Résultat du lobby: {lobby_result}")
            
            # Traiter le résultat du lobby
            lobby_action = lobby_result.get("action", "back")  # Par défaut, retour au menu
            
            if lobby_action == "quit":
                print("Fermeture du jeu depuis le lobby")
                client.disconnect()
                return {"action": "quit"}
            
            elif lobby_action == "back":
                print("Retour au menu multijoueur depuis le lobby")
                client.disconnect()
                # Arrêter le serveur car nous quittons le mode hôte
                if server_process:
                    print("Arrêt du serveur depuis le bouton retour...")
                    server_process.terminate()
                    try:
                        server_process.wait(timeout=2)
                    except:
                        if server_process.poll() is None:
                            server_process.kill()
                    print("Serveur arrêté depuis le bouton retour")
                
                # Afficher à nouveau le menu multijoueur
                menu = MainMenu()
                return menu.show_multiplayer_screen()
            
            elif lobby_action == "start_game":
                print("Démarrage de la partie depuis le lobby")
                # Créer une instance de NetworkedGUI
                print("Création de l'interface réseau...")
                gui = NetworkedGUI(game_instance, client)
                print("Interface réseau créée")
                
                print("Configuration de l'animal...")
                try:
                    # Utiliser l'écran de configuration pour créer le jeu
                    # et passer le callback pour signaler que la configuration est terminée
                    game = GUI.setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
                    # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
                    if game is None:
                        print("Configuration annulée")
                        client.disconnect()
                        return {"action": "main_menu"}
                    
                    print("Lancement de l'interface graphique...")
                    # Lancer l'interface graphique en mode réseau
                    gui.run()
                except Exception as e:
                    print(f"Erreur pendant la phase de jeu: {e}")
                    traceback.print_exc()
                finally:
                    # Déconnecter le client seulement à la fin du jeu
                    print("Déconnexion du client à la fin du jeu...")
                    client.disconnect()
                
                return {"action": "main_menu"}
        else:
            print("Impossible de se connecter au serveur local après plusieurs tentatives")
            return {"action": "main_menu"}
    
    except Exception as e:
        print(f"Erreur en mode hôte: {e}")
        traceback.print_exc()  # Afficher la trace complète
        return {"action": "main_menu"}

def get_local_ip():
    """Obtient l'adresse IP locale de la machine
    
    Returns:
        str: Adresse IP locale
    """
    try:
        # Créer un socket pour déterminer l'adresse IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Se connecter à un serveur externe (n'envoie pas réellement de données)
        s.connect(("8.8.8.8", 80))
        # Obtenir l'adresse IP locale
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"  # Fallback sur localhost

def handle_join_game(host):
    """Gère le mode client du jeu
    
    Args:
        host: Adresse IP de l'hôte
        
    Returns:
        dict: Résultat de l'action (quit, main_menu, etc.)
    """
    print("Démarrage du mode client...")
    
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
            try:
                print(f"Tentative de connexion {attempt+1}...")
                if client.connect():
                    connected = True
                    print(f"Connexion réussie à {host}")
                    break
                print(f"Tentative de connexion {attempt+1} échouée, nouvelle tentative dans 2 secondes...")
            except Exception as e:
                print(f"Erreur lors de la tentative {attempt+1}: {e}")
            
            # Attendre plus longtemps entre les tentatives
            time.sleep(2)
        
        if connected:
            print("Connecté au serveur, création de l'interface...")
            # Créer une instance de Game vide
            game_instance = Game()
            print("Instance de jeu créée")
            
            # Créer une surface pygame pour le lobby
            screen = pygame.display.set_mode((900, 600))
            pygame.display.set_caption("Jeu des Animaux - Lobby")
            
            # Créer et exécuter le lobby
            print("Affichage du lobby...")
            lobby = Lobby(screen, host, is_host=False, client=client)
            lobby_result = lobby.run()
            print(f"Résultat du lobby: {lobby_result}")
            
            # Traiter le résultat du lobby
            lobby_action = lobby_result.get("action", "back")  # Par défaut, retour au menu
            
            if lobby_action == "quit":
                print("Fermeture du jeu depuis le lobby")
                client.disconnect()
                return {"action": "quit"}
            
            elif lobby_action == "back":
                print("Retour au menu multijoueur depuis le lobby")
                client.disconnect()
                
                # Afficher à nouveau le menu multijoueur
                menu = MainMenu()
                return menu.show_multiplayer_screen()
            
            elif lobby_action == "start_game":
                print("Démarrage de la partie depuis le lobby")
                # Créer une instance de NetworkedGUI
                print("Création de l'interface réseau...")
                gui = NetworkedGUI(game_instance, client)
                print("Interface réseau créée")
                
                print("Configuration de l'animal...")
                try:
                    # Utiliser l'écran de configuration pour créer le jeu
                    # et passer le callback pour signaler que la configuration est terminée
                    game = GUI.setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
                    # Si l'utilisateur a fermé la fenêtre de configuration sans terminer
                    if game is None:
                        print("Configuration annulée")
                        client.disconnect()
                        return {"action": "main_menu"}
                    
                    print("Lancement de l'interface graphique...")
                    # Lancer l'interface graphique en mode réseau
                    gui.run()
                except Exception as e:
                    print(f"Erreur pendant la phase de jeu: {e}")
                    traceback.print_exc()
                finally:
                    # Déconnecter le client seulement à la fin du jeu
                    print("Déconnexion du client à la fin du jeu...")
                    client.disconnect()
                
                return {"action": "main_menu"}
        else:
            print(f"Impossible de se connecter au serveur {host} après plusieurs tentatives")
            # Afficher un message d'erreur à l'utilisateur
            pygame.init()
            screen = pygame.display.set_mode((900, 600))
            pygame.display.set_caption("Erreur de connexion")
            
            # Polices
            font_title = pygame.font.SysFont(None, 48)
            font_text = pygame.font.SysFont(None, 24)
            
            # Couleurs
            BLACK = (0, 0, 0)
            WHITE = (255, 255, 255)
            RED = (255, 0, 0)
            
            # Dessiner l'écran d'erreur
            screen.fill(WHITE)
            
            # Titre
            title = font_title.render("Erreur de connexion", True, RED)
            title_rect = title.get_rect(center=(450, 150))
            screen.blit(title, title_rect)
            
            # Message d'erreur
            error_msg = font_text.render(f"Impossible de se connecter au serveur {host}", True, BLACK)
            error_rect = error_msg.get_rect(center=(450, 200))
            screen.blit(error_msg, error_rect)
            
            # Instructions
            instr1 = font_text.render("Vérifiez que le serveur est en cours d'exécution", True, BLACK)
            instr1_rect = instr1.get_rect(center=(450, 240))
            screen.blit(instr1, instr1_rect)
            
            instr2 = font_text.render("et que l'adresse IP est correcte.", True, BLACK)
            instr2_rect = instr2.get_rect(center=(450, 270))
            screen.blit(instr2, instr2_rect)
            
            # Message pour continuer
            continue_msg = font_text.render("Appuyez sur une touche pour continuer...", True, BLACK)
            continue_rect = continue_msg.get_rect(center=(450, 350))
            screen.blit(continue_msg, continue_rect)
            
            pygame.display.flip()
            
            # Attendre que l'utilisateur appuie sur une touche
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return {"action": "quit"}
                    elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        waiting = False
            
            return {"action": "main_menu"}
    
    except Exception as e:
        print(f"Erreur en mode client: {e}")
        traceback.print_exc()  # Afficher la trace complète
        return {"action": "main_menu"}

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
    finally:
        cleanup() 