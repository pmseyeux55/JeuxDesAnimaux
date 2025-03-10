"""
Module pour l'écran de lobby multijoueur.
"""
import pygame
import time
from game.config import (
    WHITE, BLACK, GRAY, BLUE, RED, GREEN, LIGHT_GRAY
)

class Lobby:
    """Classe pour l'écran de lobby multijoueur"""
    
    def __init__(self, screen, host_ip, is_host=True, client=None):
        """Initialise l'écran de lobby
        
        Args:
            screen: Surface pygame pour l'affichage
            host_ip: Adresse IP de l'hôte
            is_host: True si le joueur est l'hôte, False sinon
            client: Instance de GameClient pour la communication réseau
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.host_ip = host_ip
        self.is_host = is_host
        self.client = client
        self.running = True
        self.ready = False
        self.players = []
        self.game_started = False
        
        # Si nous sommes l'hôte, nous sommes déjà dans la liste des joueurs
        if self.is_host:
            self.players.append({
                "id": 1,
                "name": "Hôte",
                "ready": False
            })
        
        # Polices
        self.title_font = pygame.font.SysFont(None, 72)
        self.subtitle_font = pygame.font.SysFont(None, 48)
        self.info_font = pygame.font.SysFont(None, 36)
        self.player_font = pygame.font.SysFont(None, 30)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Boutons
        button_width = 300
        button_height = 60
        button_x = (self.screen_width - button_width) // 2
        
        # Le bouton de démarrage n'est visible que pour l'hôte
        self.start_button = {
            "rect": pygame.Rect(button_x, self.screen_height - 150, button_width, button_height),
            "text": "Démarrer la partie" if self.is_host else "Prêt",
            "color": GREEN,
            "hover_color": (150, 255, 150),
            "active": self.is_host,  # Seul l'hôte peut démarrer la partie
            "visible": self.is_host  # Le bouton n'est visible que pour l'hôte
        }
        
        # Pour les clients, on a un bouton "Prêt" à la place
        self.ready_button = {
            "rect": pygame.Rect(button_x, self.screen_height - 150, button_width, button_height),
            "text": "Prêt",
            "color": GREEN,
            "hover_color": (150, 255, 150),
            "active": True,
            "visible": not self.is_host  # Le bouton n'est visible que pour les clients
        }
        
        self.back_button = {
            "rect": pygame.Rect(button_x, self.screen_height - 80, button_width, button_height),
            "text": "Retour",
            "color": RED,
            "hover_color": (255, 150, 150),
            "active": True,
            "visible": True
        }
        
        # Créer un rectangle de mise en évidence pour l'adresse IP
        self.ip_highlight_rect = pygame.Rect(
            (self.screen_width - 500) // 2,
            120,
            500,
            60
        )
        
        # Ajouter des informations de connexion supplémentaires
        self.connection_info = "Pour que d'autres joueurs puissent se connecter:"
        self.connection_info_local = f"- Sur le même réseau: {host_ip}"
        self.connection_info_external = "- Sur un réseau différent: Votre IP publique"
        self.connection_info_port = "- Le port 5555 doit être ouvert dans votre pare-feu"
        
        # Dernière mise à jour des joueurs
        self.last_update = time.time()
        self.update_interval = 1.0  # Mettre à jour la liste des joueurs toutes les secondes
        
        # Message d'information
        if self.is_host:
            self.info_message = "En attente de joueurs..."
        else:
            self.info_message = "En attente que l'hôte démarre la partie..."
        
    def run(self):
        """Exécute la boucle principale du lobby
        
        Returns:
            dict: Informations sur l'action choisie par l'utilisateur
        """
        clock = pygame.time.Clock()
        result = {"action": "back"}  # Valeur par défaut si la boucle est interrompue
        
        print(f"Démarrage du lobby (hôte: {self.is_host})")
        
        while self.running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Événement QUIT détecté")
                    self.running = False
                    result = {"action": "quit"}
                    break
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Gérer les clics de souris
                    if event.button == 1:  # Clic gauche
                        mouse_pos = event.pos
                        print(f"Clic à la position {mouse_pos}")
                        
                        # Vérifier si le bouton de retour a été cliqué
                        if self.back_button["rect"].collidepoint(mouse_pos):
                            print(f"Bouton retour cliqué (rect: {self.back_button['rect']})")
                            self.running = False
                            result = {"action": "back"}
                            break
                        
                        # Vérifier si le bouton de démarrage a été cliqué (seulement pour l'hôte)
                        elif self.is_host and self.start_button["visible"] and self.start_button["active"] and self.start_button["rect"].collidepoint(mouse_pos):
                            print("Bouton démarrer cliqué")
                            # L'hôte démarre la partie
                            self.running = False
                            
                            # Informer les clients que la partie commence
                            if self.client:
                                if not self.client.connected:
                                    print("Client non connecté, tentative de reconnexion...")
                                    if not self.client.reconnect():
                                        print("Échec de la reconnexion, impossible d'envoyer le signal de démarrage")
                                        self.info_message = "Erreur de connexion. Tentative de reconnexion..."
                                        continue
                                    print("Reconnexion réussie, envoi du signal de démarrage...")
                                
                                # Envoyer le signal de démarrage au serveur
                                if not self.client.send_action({"game_started": True}):
                                    print("Échec de l'envoi du signal de démarrage")
                                    self.info_message = "Erreur de connexion. Tentative de reconnexion..."
                                    continue
                            
                            result = {"action": "start_game"}
                            break
                        
                        # Vérifier si le bouton "Prêt" a été cliqué (seulement pour les clients)
                        elif not self.is_host and self.ready_button["visible"] and self.ready_button["active"] and self.ready_button["rect"].collidepoint(mouse_pos):
                            print("Bouton prêt cliqué")
                            # Le client se marque comme prêt
                            self.ready = not self.ready
                            self.ready_button["text"] = "Annuler" if self.ready else "Prêt"
                            self.ready_button["color"] = RED if self.ready else GREEN
                            self.ready_button["hover_color"] = (255, 150, 150) if self.ready else (150, 255, 150)
                            
                            # Informer le serveur que nous sommes prêts
                            if self.client:
                                if not self.client.connected:
                                    print("Client non connecté, tentative de reconnexion...")
                                    if not self.client.reconnect():
                                        print("Échec de la reconnexion, impossible d'envoyer le statut")
                                        self.info_message = "Erreur de connexion. Tentative de reconnexion..."
                                        continue
                                    print("Reconnexion réussie, envoi du statut...")
                                
                                # Envoyer le statut au serveur
                                if not self.client.send_action({"ready": self.ready}):
                                    print("Échec de l'envoi du statut")
                                    self.info_message = "Erreur de connexion. Tentative de reconnexion..."
                                    continue
            
            # Si la boucle a été interrompue, sortir
            if not self.running:
                break
            
            # Mettre à jour la liste des joueurs
            current_time = time.time()
            if current_time - self.last_update > self.update_interval:
                self.update_players()
                self.last_update = current_time
            
            # Vérifier si la partie a commencé (pour les clients)
            if not self.is_host and self.game_started:
                print("La partie a commencé (détecté par le client)")
                self.running = False
                result = {"action": "start_game"}
                break
            
            # Mettre à jour l'affichage
            self.screen.fill(WHITE)
            
            # Dessiner le titre
            title = self.title_font.render("Lobby Multijoueur", True, BLACK)
            title_rect = title.get_rect(center=(self.screen_width // 2, 60))
            self.screen.blit(title, title_rect)
            
            # Dessiner un rectangle de mise en évidence pour l'adresse IP
            pygame.draw.rect(self.screen, (230, 230, 255), self.ip_highlight_rect)
            pygame.draw.rect(self.screen, BLUE, self.ip_highlight_rect, 2)
            
            # Dessiner l'adresse IP en gros et en gras
            ip_text = self.subtitle_font.render(f"Adresse IP: {self.host_ip}", True, BLUE)
            ip_rect = ip_text.get_rect(center=self.ip_highlight_rect.center)
            self.screen.blit(ip_text, ip_rect)
            
            # Dessiner les informations de connexion supplémentaires (seulement pour l'hôte)
            if self.is_host:
                info_y = self.ip_highlight_rect.bottom + 10
                
                # Titre des informations de connexion
                info_text = self.small_font.render(self.connection_info, True, BLACK)
                info_rect = info_text.get_rect(center=(self.screen_width // 2, info_y))
                self.screen.blit(info_text, info_rect)
                
                # Informations sur le réseau local
                info_y += 25
                local_text = self.small_font.render(self.connection_info_local, True, BLACK)
                local_rect = local_text.get_rect(center=(self.screen_width // 2, info_y))
                self.screen.blit(local_text, local_rect)
                
                # Informations sur le réseau externe
                info_y += 25
                external_text = self.small_font.render(self.connection_info_external, True, BLACK)
                external_rect = external_text.get_rect(center=(self.screen_width // 2, info_y))
                self.screen.blit(external_text, external_rect)
                
                # Informations sur le port
                info_y += 25
                port_text = self.small_font.render(self.connection_info_port, True, BLACK)
                port_rect = port_text.get_rect(center=(self.screen_width // 2, info_y))
                self.screen.blit(port_text, port_rect)
            
            # Dessiner le sous-titre pour la liste des joueurs
            subtitle = self.subtitle_font.render("Joueurs connectés:", True, BLACK)
            subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 220))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Dessiner la liste des joueurs
            player_y = 270
            for player in self.players:
                # Dessiner un rectangle pour le joueur
                player_rect = pygame.Rect(
                    (self.screen_width - 400) // 2,
                    player_y,
                    400,
                    40
                )
                pygame.draw.rect(self.screen, LIGHT_GRAY, player_rect)
                pygame.draw.rect(self.screen, BLACK, player_rect, 1)
                
                # Dessiner le nom du joueur
                player_name = f"Joueur {player['id']}: {player['name']}"
                player_text = self.player_font.render(player_name, True, BLACK)
                player_text_rect = player_text.get_rect(midleft=(player_rect.left + 20, player_rect.centery))
                self.screen.blit(player_text, player_text_rect)
                
                # Dessiner le statut du joueur
                status_text = self.player_font.render(
                    "Prêt" if player.get("ready", False) else "En attente",
                    True,
                    GREEN if player.get("ready", False) else RED
                )
                status_rect = status_text.get_rect(midright=(player_rect.right - 20, player_rect.centery))
                self.screen.blit(status_text, status_rect)
                
                player_y += 50
            
            # Dessiner le message d'information
            info_text = self.info_font.render(self.info_message, True, BLACK)
            info_rect = info_text.get_rect(center=(self.screen_width // 2, self.screen_height - 200))
            self.screen.blit(info_text, info_rect)
            
            # Dessiner les boutons
            # Mettre à jour l'état des boutons
            mouse_pos = pygame.mouse.get_pos()
            
            # Bouton de démarrage (seulement pour l'hôte)
            if self.is_host and self.start_button["visible"]:
                start_color = self.start_button["hover_color"] if self.start_button["rect"].collidepoint(mouse_pos) else self.start_button["color"]
                pygame.draw.rect(self.screen, start_color, self.start_button["rect"])
                pygame.draw.rect(self.screen, BLACK, self.start_button["rect"], 2)
                
                start_text = self.info_font.render(self.start_button["text"], True, WHITE)
                start_text_rect = start_text.get_rect(center=self.start_button["rect"].center)
                self.screen.blit(start_text, start_text_rect)
            
            # Bouton "Prêt" (seulement pour les clients)
            if not self.is_host and self.ready_button["visible"]:
                ready_color = self.ready_button["hover_color"] if self.ready_button["rect"].collidepoint(mouse_pos) else self.ready_button["color"]
                pygame.draw.rect(self.screen, ready_color, self.ready_button["rect"])
                pygame.draw.rect(self.screen, BLACK, self.ready_button["rect"], 2)
                
                ready_text = self.info_font.render(self.ready_button["text"], True, WHITE)
                ready_text_rect = ready_text.get_rect(center=self.ready_button["rect"].center)
                self.screen.blit(ready_text, ready_text_rect)
            
            # Bouton de retour
            back_color = self.back_button["hover_color"] if self.back_button["rect"].collidepoint(mouse_pos) else self.back_button["color"]
            pygame.draw.rect(self.screen, back_color, self.back_button["rect"])
            pygame.draw.rect(self.screen, BLACK, self.back_button["rect"], 2)
            
            back_text = self.info_font.render(self.back_button["text"], True, WHITE)
            back_text_rect = back_text.get_rect(center=self.back_button["rect"].center)
            self.screen.blit(back_text, back_text_rect)
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            clock.tick(60)
        
        print(f"Sortie du lobby avec résultat: {result}")
        return result
    
    def update_players(self):
        """Met à jour la liste des joueurs connectés"""
        # Si nous avons un client, demander la liste des joueurs au serveur
        if self.client:
            if not self.client.connected:
                print("Client non connecté, tentative de reconnexion...")
                if not self.client.reconnect():
                    print("Échec de la reconnexion, impossible de mettre à jour les joueurs")
                    return
                print("Reconnexion réussie, mise à jour des joueurs...")
            
            # Vérifier si nous avons reçu des mises à jour de l'état du jeu
            game_state = self.client.game_state
            if game_state:
                # Vérifier si la partie a commencé
                if "game_started" in game_state and game_state["game_started"]:
                    self.game_started = True
                    if not self.is_host:
                        self.info_message = "L'hôte a démarré la partie. Préparation en cours..."
                
                # Mettre à jour la liste des joueurs
                if "players" in game_state:
                    self.players = game_state["players"]
                    
                    # Mettre à jour le message d'information
                    if self.is_host:
                        # Vérifier si tous les joueurs sont prêts
                        all_ready = all(player.get("ready", False) for player in self.players if player["id"] != 1)
                        if len(self.players) > 1 and all_ready:
                            self.info_message = "Tous les joueurs sont prêts. Vous pouvez démarrer la partie."
                            self.start_button["active"] = True
                        else:
                            self.info_message = "En attente que tous les joueurs soient prêts..."
                            self.start_button["active"] = len(self.players) > 1
            
            # Envoyer notre statut au serveur
            if not self.is_host and self.client.connected:
                self.client.send_action({"ready": self.ready})
        
        # Si nous sommes l'hôte et qu'il n'y a pas de client, simuler des joueurs pour les tests
        elif self.is_host and not self.client:
            # Ajouter un joueur toutes les 5 secondes pour les tests
            if len(self.players) < 4 and time.time() % 5 < 0.1:
                self.players.append({
                    "id": len(self.players) + 1,
                    "name": f"Joueur {len(self.players) + 1}",
                    "ready": False
                })
            
            # Marquer les joueurs comme prêts aléatoirement
            for player in self.players:
                if player["id"] != 1 and time.time() % 7 < 0.1:
                    player["ready"] = not player.get("ready", False)
            
            # Mettre à jour le message d'information
            all_ready = all(player.get("ready", False) for player in self.players if player["id"] != 1)
            if len(self.players) > 1 and all_ready:
                self.info_message = "Tous les joueurs sont prêts. Vous pouvez démarrer la partie."
                self.start_button["active"] = True
            else:
                self.info_message = "En attente que tous les joueurs soient prêts..."
                self.start_button["active"] = len(self.players) > 1 