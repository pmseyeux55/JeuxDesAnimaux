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
        self.ip_font = pygame.font.SysFont(None, 36)  # Police plus grande pour l'IP
        
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
            "Pour jouer en multijoueur:",
            "",
            "1. Un joueur doit héberger la partie (cliquez sur 'Héberger une partie')",
            "2. L'autre joueur doit rejoindre en entrant l'IP de l'hôte ci-dessous",
            "",
            "Si vous êtes l'hôte, partagez votre adresse IP avec l'autre joueur.",
            "Si vous êtes le client, entrez l'adresse IP de l'hôte dans le champ ci-dessous."
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
                "hover_color": (150, 255, 150),
                "original_text": "Rejoindre une partie"  # Sauvegarder le texte original
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
        
        # Rectangle pour mettre en évidence l'adresse IP
        self.ip_highlight_rect = pygame.Rect(
            (self.screen_width - 300) // 2,
            230,
            300,
            40
        )
    
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
                                        # Au lieu de quitter immédiatement, activer le champ de saisie
                                        # et changer le texte du bouton pour "Confirmer"
                                        self.ip_input["active"] = True
                                        button["text"] = "Confirmer la connexion"
                                        button["action"] = "confirm_join"
                                        # Mettre à jour le texte d'information
                                        self.multiplayer_info.append("Entrez l'adresse IP et cliquez sur 'Confirmer la connexion'")
                                    elif action == "confirm_join":
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
        # Dessiner le titre
        title = self.title_font.render("Mode Multijoueur", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Dessiner un rectangle de mise en évidence pour l'adresse IP
        ip_highlight_rect = pygame.Rect(
            (self.screen_width - 400) // 2,
            120,
            400,
            50
        )
        pygame.draw.rect(self.screen, (230, 230, 255), ip_highlight_rect)
        pygame.draw.rect(self.screen, BLUE, ip_highlight_rect, 2)
        
        # Dessiner l'adresse IP en gros et en gras
        ip_font = pygame.font.SysFont(None, 36)
        ip_text = ip_font.render(f"Votre IP: {self.local_ip}", True, BLUE)
        ip_rect = ip_text.get_rect(center=ip_highlight_rect.center)
        self.screen.blit(ip_text, ip_rect)
        
        # Dessiner les informations
        y_offset = 180
        for line in self.multiplayer_info:
            text = self.info_font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # Dessiner le champ de saisie avec un texte explicatif au-dessus
        if self.ip_input["active"] or any(button["action"] == "confirm_join" for button in self.multiplayer_buttons):
            # Dessiner le texte "Entrez l'adresse IP:" au-dessus du champ
            ip_label = self.info_font.render("Entrez l'adresse IP du serveur:", True, BLUE)
            ip_label_rect = ip_label.get_rect(center=(self.screen_width // 2, self.ip_input["rect"].top - 20))
            self.screen.blit(ip_label, ip_label_rect)
        
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
    
    def show_multiplayer_screen(self):
        """Affiche directement l'écran multijoueur et retourne le résultat"""
        self.current_screen = "multiplayer"
        self.reset_multiplayer_screen()
        return self.run()
    
    def reset_multiplayer_screen(self):
        """Réinitialise l'écran multijoueur à son état initial"""
        # Réinitialiser le champ de saisie
        self.ip_input["text"] = ""
        self.ip_input["active"] = False
        
        # Réinitialiser les boutons
        for button in self.multiplayer_buttons:
            if "original_text" in button:
                button["text"] = button["original_text"]
                button["action"] = "join_game"
        
        # Réinitialiser les informations
        self.multiplayer_info = [
            "Pour jouer en multijoueur:",
            "",
            "1. Un joueur doit héberger la partie (cliquez sur 'Héberger une partie')",
            "2. L'autre joueur doit rejoindre en entrant l'IP de l'hôte ci-dessous",
            "",
            "Si vous êtes l'hôte, partagez votre adresse IP avec l'autre joueur.",
            "Si vous êtes le client, entrez l'adresse IP de l'hôte dans le champ ci-dessous."
        ] 