"""
Module pour l'écran de menu principal du jeu.
"""
import pygame
import sys
import socket
from game.config import (
    WHITE, BLACK, GRAY, BLUE, RED, GREEN,
    LIGHT_GRAY
)

class MainMenu:
    """Classe pour l'écran de menu principal"""
    
    def __init__(self, screen_width=900, screen_height=600):
        """Initialise l'écran de menu
        
        Args:
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Jeu des Animaux - Menu Principal")
        
        # Polices
        self.title_font = pygame.font.SysFont(None, 72)
        self.button_font = pygame.font.SysFont(None, 48)
        self.info_font = pygame.font.SysFont(None, 24)
        
        # Boutons
        button_width = 300
        button_height = 60
        button_margin = 20
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            {
                "rect": pygame.Rect(button_x, 200, button_width, button_height),
                "text": "Mode Solo",
                "action": "single_player",
                "color": BLUE,
                "hover_color": (150, 150, 255)
            },
            {
                "rect": pygame.Rect(button_x, 200 + button_height + button_margin, button_width, button_height),
                "text": "Mode Multijoueur",
                "action": "multiplayer",
                "color": GREEN,
                "hover_color": (150, 255, 150)
            },
            {
                "rect": pygame.Rect(button_x, 200 + 2 * (button_height + button_margin), button_width, button_height),
                "text": "Options",
                "action": "options",
                "color": GRAY,
                "hover_color": (200, 200, 200)
            },
            {
                "rect": pygame.Rect(button_x, 200 + 3 * (button_height + button_margin), button_width, button_height),
                "text": "Quitter",
                "action": "quit",
                "color": RED,
                "hover_color": (255, 150, 150)
            }
        ]
        
        # État du menu
        self.current_screen = "main"  # "main", "multiplayer", "options"
        self.selected_button = None
        self.running = True
        
        # Obtenir l'adresse IP locale
        self.local_ip = self.get_local_ip()
        
        # Informations pour l'écran multijoueur
        self.multiplayer_info = [
            f"Votre adresse IP: {self.local_ip}",
            "Port: 5555",
            "",
            "Partagez ces informations avec votre ami pour qu'il puisse se connecter.",
            "",
            "Appuyez sur 'Héberger une partie' pour démarrer le serveur.",
            "Votre ami doit utiliser './client.py --host VOTRE_IP' pour se connecter."
        ]
        
        # Boutons pour l'écran multijoueur
        self.multiplayer_buttons = [
            {
                "rect": pygame.Rect(button_x, 350, button_width, button_height),
                "text": "Héberger une partie",
                "action": "host_game",
                "color": BLUE,
                "hover_color": (150, 150, 255)
            },
            {
                "rect": pygame.Rect(button_x, 350 + button_height + button_margin, button_width, button_height),
                "text": "Rejoindre une partie",
                "action": "join_game",
                "color": GREEN,
                "hover_color": (150, 255, 150)
            },
            {
                "rect": pygame.Rect(button_x, 350 + 2 * (button_height + button_margin), button_width, button_height),
                "text": "Retour",
                "action": "back_to_main",
                "color": GRAY,
                "hover_color": (200, 200, 200)
            }
        ]
        
        # Champ de saisie pour l'adresse IP
        self.ip_input = {
            "rect": pygame.Rect(button_x, 300, button_width, button_height),
            "text": "",
            "active": False,
            "placeholder": "Adresse IP du serveur"
        }
    
    def get_local_ip(self):
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
    
    def run(self):
        """Exécute la boucle principale du menu
        
        Returns:
            dict: Informations sur l'action choisie par l'utilisateur
        """
        clock = pygame.time.Clock()
        
        while self.running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return {"action": "quit"}
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Gérer les clics de souris
                    if event.button == 1:  # Clic gauche
                        if self.current_screen == "main":
                            for button in self.buttons:
                                if button["rect"].collidepoint(event.pos):
                                    action = button["action"]
                                    
                                    if action == "quit":
                                        self.running = False
                                        return {"action": "quit"}
                                    elif action == "single_player":
                                        self.running = False
                                        return {"action": "single_player"}
                                    elif action == "multiplayer":
                                        self.current_screen = "multiplayer"
                                    elif action == "options":
                                        self.current_screen = "options"
                        
                        elif self.current_screen == "multiplayer":
                            # Vérifier si le champ de saisie a été cliqué
                            if self.ip_input["rect"].collidepoint(event.pos):
                                self.ip_input["active"] = True
                            else:
                                self.ip_input["active"] = False
                            
                            # Vérifier si un bouton a été cliqué
                            for button in self.multiplayer_buttons:
                                if button["rect"].collidepoint(event.pos):
                                    action = button["action"]
                                    
                                    if action == "back_to_main":
                                        self.current_screen = "main"
                                    elif action == "host_game":
                                        self.running = False
                                        return {"action": "host_game"}
                                    elif action == "join_game":
                                        self.running = False
                                        return {
                                            "action": "join_game",
                                            "host": self.ip_input["text"] if self.ip_input["text"] else "localhost"
                                        }
                        
                        elif self.current_screen == "options":
                            # Pour l'instant, juste retourner au menu principal
                            self.current_screen = "main"
                
                elif event.type == pygame.KEYDOWN:
                    # Gérer les touches du clavier
                    if self.current_screen == "multiplayer" and self.ip_input["active"]:
                        if event.key == pygame.K_BACKSPACE:
                            # Supprimer le dernier caractère
                            self.ip_input["text"] = self.ip_input["text"][:-1]
                        elif event.key == pygame.K_RETURN:
                            # Désactiver le champ de saisie
                            self.ip_input["active"] = False
                        else:
                            # Ajouter le caractère
                            self.ip_input["text"] += event.unicode
                
                elif event.type == pygame.MOUSEMOTION:
                    # Mettre à jour le bouton survolé
                    self.selected_button = None
                    
                    if self.current_screen == "main":
                        for button in self.buttons:
                            if button["rect"].collidepoint(event.pos):
                                self.selected_button = button
                    
                    elif self.current_screen == "multiplayer":
                        for button in self.multiplayer_buttons:
                            if button["rect"].collidepoint(event.pos):
                                self.selected_button = button
            
            # Dessiner l'écran
            self.draw()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            
            # Limiter à 60 FPS
            clock.tick(60)
        
        return {"action": "quit"}
    
    def draw(self):
        """Dessine l'écran de menu"""
        # Effacer l'écran
        self.screen.fill(WHITE)
        
        # Dessiner le titre
        title_text = self.title_font.render("Jeu des Animaux", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Dessiner l'écran approprié
        if self.current_screen == "main":
            self.draw_main_screen()
        elif self.current_screen == "multiplayer":
            self.draw_multiplayer_screen()
        elif self.current_screen == "options":
            self.draw_options_screen()
    
    def draw_main_screen(self):
        """Dessine l'écran principal du menu"""
        # Dessiner les boutons
        for button in self.buttons:
            # Déterminer la couleur du bouton
            color = button["hover_color"] if button == self.selected_button else button["color"]
            
            # Dessiner le bouton
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, BLACK, button["rect"], 2)
            
            # Dessiner le texte du bouton
            text = self.button_font.render(button["text"], True, WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
    
    def draw_multiplayer_screen(self):
        """Dessine l'écran multijoueur"""
        # Dessiner les informations
        y_offset = 150
        for line in self.multiplayer_info:
            text = self.info_font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # Dessiner le champ de saisie
        pygame.draw.rect(self.screen, WHITE, self.ip_input["rect"])
        pygame.draw.rect(self.screen, BLACK if not self.ip_input["active"] else BLUE, self.ip_input["rect"], 2)
        
        # Dessiner le texte du champ de saisie ou le placeholder
        if self.ip_input["text"]:
            text = self.info_font.render(self.ip_input["text"], True, BLACK)
        else:
            text = self.info_font.render(self.ip_input["placeholder"], True, LIGHT_GRAY)
        
        text_rect = text.get_rect(center=self.ip_input["rect"].center)
        self.screen.blit(text, text_rect)
        
        # Dessiner les boutons
        for button in self.multiplayer_buttons:
            # Déterminer la couleur du bouton
            color = button["hover_color"] if button == self.selected_button else button["color"]
            
            # Dessiner le bouton
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, BLACK, button["rect"], 2)
            
            # Dessiner le texte du bouton
            text = self.button_font.render(button["text"], True, WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
    
    def draw_options_screen(self):
        """Dessine l'écran d'options"""
        # Pour l'instant, juste afficher un message
        text = self.info_font.render("Options (à venir)", True, BLACK)
        text_rect = text.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(text, text_rect)
        
        # Dessiner un bouton de retour
        back_button = {
            "rect": pygame.Rect((self.screen_width - 200) // 2, 350, 200, 50),
            "text": "Retour",
            "color": GRAY,
            "hover_color": (200, 200, 200)
        }
        
        # Déterminer la couleur du bouton
        color = back_button["hover_color"] if self.selected_button == back_button else back_button["color"]
        
        # Dessiner le bouton
        pygame.draw.rect(self.screen, color, back_button["rect"])
        pygame.draw.rect(self.screen, BLACK, back_button["rect"], 2)
        
        # Dessiner le texte du bouton
        text = self.button_font.render(back_button["text"], True, WHITE)
        text_rect = text.get_rect(center=back_button["rect"].center)
        self.screen.blit(text, text_rect) 