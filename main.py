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
from ui.setup_screen_fix import fixed_setup_game  # Importer la version corrigée

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
                game = fixed_setup_game()
                
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
        time.sleep(2)  # Attendre un peu plus longtemps pour s'assurer que le serveur est prêt
        
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
        # Se connecter au serveur
        client = GameClient("127.0.0.1")
        
        # Essayer de se connecter plusieurs fois
        connected = False
        for attempt in range(5):  # Augmenter le nombre de tentatives
            try:
                print(f"Tentative de connexion {attempt+1}...")
                if client.connect():
                    connected = True
                    print(f"Connexion réussie à 127.0.0.1")
                    break
                print(f"Tentative de connexion {attempt+1} échouée, nouvelle tentative dans 2 secondes...")
                time.sleep(2)  # Attendre un peu plus entre les tentatives
            except Exception as e:
                print(f"Erreur lors de la tentative {attempt+1}: {e}")
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
                
                # Vérifier si le client est toujours connecté
                if not client.connected:
                    print("Client déconnecté, création d'une nouvelle connexion...")
                    # Créer un nouveau client
                    client = GameClient("127.0.0.1")
                    
                    # Essayer de se connecter plusieurs fois
                    connected = False
                    for attempt in range(5):
                        try:
                            print(f"Tentative de connexion {attempt+1}...")
                            if client.connect():
                                connected = True
                                print(f"Connexion réussie à 127.0.0.1")
                                break
                            print(f"Tentative de connexion {attempt+1} échouée, nouvelle tentative dans 2 secondes...")
                            time.sleep(2)
                        except Exception as e:
                            print(f"Erreur lors de la tentative {attempt+1}: {e}")
                            time.sleep(2)
                    
                    if not connected:
                        print("Impossible de se connecter au serveur après plusieurs tentatives")
                        return {"action": "main_menu"}
                
                # Créer une instance de NetworkedGUI
                print("Création de l'interface réseau...")
                gui = NetworkedGUI(game_instance, client)
                print("Interface réseau créée")
                
                print("Configuration de l'animal...")
                try:
                    # Utiliser l'écran de configuration pour créer le jeu
                    # et passer le callback pour signaler que la configuration est terminée
                    game = fixed_setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
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
                    game = fixed_setup_game(setup_complete_callback=gui.setup_complete_callback)
                    
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

def fixed_setup_game(screen_width=900, screen_height=600, setup_complete_callback=None):
    """Version corrigée de la méthode setup_game qui gère correctement l'attribut button_font.
    
    Args:
        screen_width: Largeur de l'écran
        screen_height: Hauteur de l'écran
        setup_complete_callback: Fonction à appeler lorsque la configuration est terminée
        
    Returns:
        Game: Instance du jeu configuré, ou None si l'utilisateur a annulé
    """
    # Initialiser pygame si ce n'est pas déjà fait
    if not pygame.get_init():
        pygame.init()
    
    # Créer et exécuter l'écran de configuration des animaux
    from ui.gui import SetupScreen, Button
    setup_screen = SetupScreen(screen_width, screen_height)
    
    # S'assurer que button_font est initialisé
    setup_screen.button_font = pygame.font.SysFont(None, 30)
    
    # En mode multijoueur, on ne configure qu'un seul animal
    if setup_complete_callback:
        # Remplacer la méthode run_single_player par une version corrigée
        def fixed_run_single_player(self):
            """Version corrigée de run_single_player qui gère correctement button_font"""
            # Vérifier que la police des boutons est initialisée
            if not hasattr(self, 'button_font') or self.button_font is None:
                print("Initialisation de button_font dans fixed_run_single_player")
                self.button_font = pygame.font.SysFont(None, 30)
                
            # Créer un bouton de démarrage
            button_width = 200
            button_height = 50
            button_x = (self.screen_width - button_width) // 2
            button_y = self.screen_height - 100
            self.start_button = Button(button_x, button_y, button_width, button_height, "Démarrer", GREEN, (150, 255, 150))
            
            running = True
            while running:
                # Gérer les événements
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    
                    # Gérer les clics de souris
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Clic gauche
                            # Vérifier si le bouton de démarrage a été cliqué
                            if self.start_button.is_hovered(pygame.mouse.get_pos()):
                                # Retourner les données de configuration
                                return self.get_player_data()
                    
                    # Gérer les événements des sliders
                    for slider in self.sliders:
                        slider.handle_event(event)
                    
                    # Gérer les événements des boutons fléchés
                    for button in self.arrow_buttons:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if button["rect"].collidepoint(event.pos):
                                self.handle_stat_change(button["stat"], button["change"])
                
                # Mettre à jour les sliders
                mouse_pos = pygame.mouse.get_pos()
                for slider in self.sliders:
                    slider.update(mouse_pos)
                
                # Mettre à jour le bouton de démarrage
                self.start_button.update(mouse_pos)
                
                # Mettre à jour les points restants
                self.update_remaining_points()
                
                # Dessiner l'écran
                self.screen.fill(WHITE)
                
                # Dessiner le titre
                title = self.title_font.render("Configuration de l'Animal", True, BLACK)
                title_rect = title.get_rect(center=(self.screen_width // 2, 30))
                self.screen.blit(title, title_rect)
                
                # Dessiner le tableau de configuration
                self.draw_table()
                
                # Vérifier à nouveau que button_font est initialisé avant de dessiner le bouton
                if not hasattr(self, 'button_font') or self.button_font is None:
                    print("Réinitialisation de button_font avant de dessiner le bouton")
                    self.button_font = pygame.font.SysFont(None, 30)
                
                try:
                    # Dessiner le bouton de démarrage avec gestion d'erreur
                    self.start_button.draw(self.screen, self.button_font)
                except AttributeError as e:
                    print(f"Erreur lors du dessin du bouton: {e}")
                    # Si button_font n'est pas défini, le créer
                    self.button_font = pygame.font.SysFont(None, 30)
                    self.start_button.draw(self.screen, self.button_font)
                
                # Mettre à jour l'affichage
                pygame.display.flip()
                self.clock.tick(60)
            
            return None  # Si la boucle est interrompue
        
        # Remplacer la méthode run_single_player par notre version corrigée
        import types
        setup_screen.run_single_player = types.MethodType(fixed_run_single_player, setup_screen)
        
        player_data = setup_screen.run_single_player()
        opponent_data = None
    else:
        player_data, opponent_data = setup_screen.run()
    
    # Si l'utilisateur a fermé la fenêtre sans terminer
    if player_data is None:
        return None
    
    # Créer un nouveau jeu
    from game.game import Game
    from game.animal import Animal
    from game.resources import Fruit, GreenFruit, RedFruit
    from game.config import (
        HP_CONVERSION, STAMINA_CONVERSION, SPEED_CONVERSION, TEETH_CONVERSION, 
        CLAWS_CONVERSION, SKIN_CONVERSION, HEIGHT_CONVERSION
    )
    
    game = Game()
    
    # Extraire les données des animaux
    player_name = player_data["name"]
    player_hp = player_data["hp"] / HP_CONVERSION
    player_stamina = player_data["stamina"] / STAMINA_CONVERSION
    player_speed = player_data["speed"] / SPEED_CONVERSION
    player_teeth = player_data["teeth"] / TEETH_CONVERSION
    player_claws = player_data["claws"] / CLAWS_CONVERSION
    player_skin = player_data["skin"] / SKIN_CONVERSION
    player_height = player_data["height"] / HEIGHT_CONVERSION
    player_position = player_data["position"]
    
    # Créer l'animal du joueur
    player_animal = Animal(
        player_name,
        player_hp,
        player_stamina,
        player_speed,
        player_position,
        player_teeth,
        player_claws,
        player_skin,
        player_height
    )
    
    # Ajouter l'animal du joueur au jeu
    game.add_animal(player_animal, player_position)
    
    # En mode solo, ajouter l'animal de l'adversaire
    if opponent_data:
        opponent_name = opponent_data["name"]
        opponent_hp = opponent_data["hp"] / HP_CONVERSION
        opponent_stamina = opponent_data["stamina"] / STAMINA_CONVERSION
        opponent_speed = opponent_data["speed"] / SPEED_CONVERSION
        opponent_teeth = opponent_data["teeth"] / TEETH_CONVERSION
        opponent_claws = opponent_data["claws"] / CLAWS_CONVERSION
        opponent_skin = opponent_data["skin"] / SKIN_CONVERSION
        opponent_height = opponent_data["height"] / HEIGHT_CONVERSION
        opponent_position = opponent_data["position"]
        
        # Créer l'animal de l'adversaire
        opponent_animal = Animal(
            opponent_name,
            opponent_hp,
            opponent_stamina,
            opponent_speed,
            opponent_position,
            opponent_teeth,
            opponent_claws,
            opponent_skin,
            opponent_height
        )
        
        # Ajouter l'animal de l'adversaire au jeu
        game.add_animal(opponent_animal, opponent_position)
    
    # Ajouter des fruits au jeu
    for position in [(5, 5), (10, 10), (15, 15)]:
        fruit = Fruit(position=position)
        game.add_resource(fruit, position)
    
    # Si un callback a été fourni, l'appeler
    if setup_complete_callback:
        setup_complete_callback(game)
    
    return game

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
    finally:
        cleanup() 