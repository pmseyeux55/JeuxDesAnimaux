"""
Module pour corriger les problèmes avec la classe SetupScreen.
"""
import pygame
from game.config import (
    WHITE, BLACK, GRAY, BLUE, RED, GREEN, LIGHT_GRAY, YELLOW, ORANGE, BROWN, DARK_BLUE,
    MAX_POINTS, HP_MIN, STAMINA_MIN, SPEED_MIN, TEETH_MIN, CLAWS_MIN, SKIN_MIN, HEIGHT_MIN,
    HP_CONVERSION, STAMINA_CONVERSION, SPEED_CONVERSION, TEETH_CONVERSION, CLAWS_CONVERSION, SKIN_CONVERSION, HEIGHT_CONVERSION
)
from ui.gui import SetupScreen, Button

class FixedSetupScreen(SetupScreen):
    """Version corrigée de la classe SetupScreen qui gère correctement l'attribut button_font."""
    
    def __init__(self, screen_width, screen_height):
        """Initialise l'écran de configuration avec une police de bouton correctement définie.
        
        Args:
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
        """
        # Appeler le constructeur parent
        super().__init__(screen_width, screen_height)
        
        # S'assurer que button_font est initialisé
        self.button_font = pygame.font.SysFont(None, 30)
        print("FixedSetupScreen: button_font initialisé dans __init__")
        
        # Initialiser les sliders (qui sont utilisés mais jamais initialisés dans SetupScreen)
        self.sliders = []
        print("FixedSetupScreen: sliders initialisé dans __init__")
        
        # Initialiser arrow_buttons (qui est utilisé mais jamais initialisé dans SetupScreen)
        self.arrow_buttons = []
        
        try:
            # Créer les boutons fléchés pour chaque statistique
            stats = ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]
            for stat in stats:
                # Vérifier que les boutons existent
                if hasattr(self, 'minus_buttons') and hasattr(self, 'plus_buttons'):
                    if stat in self.minus_buttons and stat in self.plus_buttons:
                        # Bouton pour diminuer la statistique
                        self.arrow_buttons.append({"stat": stat, "change": -1, "rect": self.minus_buttons[stat].rect})
                        # Bouton pour augmenter la statistique
                        self.arrow_buttons.append({"stat": stat, "change": 1, "rect": self.plus_buttons[stat].rect})
            
            print("FixedSetupScreen: arrow_buttons initialisé dans __init__")
        except Exception as e:
            print(f"Erreur lors de l'initialisation des arrow_buttons: {e}")
            # Créer des arrow_buttons vides en cas d'erreur
            self.arrow_buttons = []
    
    def get_player_data(self):
        """Récupère les données de configuration du joueur.
        
        Returns:
            dict: Données de configuration du joueur
        """
        # Récupérer les paramètres de l'animal actuel
        if self.current_phase == 1:
            params = self.player1_animal_params
            name = self.player1_animal_name
            position = LION_START_POSITION
        else:  # Phase 2
            params = self.player2_animal_params
            name = self.player2_animal_name
            position = TIGER_START_POSITION
        
        # Créer un dictionnaire avec les données de configuration
        player_data = {
            "name": name,
            "hp": params["hp"],
            "stamina": params["stamina"],
            "speed": params["speed"],
            "teeth": params["teeth"],
            "claws": params["claws"],
            "skin": params["skin"],
            "height": params["height"],
            "position": position
        }
        
        return player_data
    
    def run_single_player(self):
        """Exécute l'écran de configuration pour un seul joueur avec une gestion robuste de button_font.
        
        Returns:
            dict: Données de configuration du joueur, ou None si l'utilisateur a annulé
        """
        # Vérifier que la police des boutons est initialisée
        if not hasattr(self, 'button_font') or self.button_font is None:
            print("FixedSetupScreen: Initialisation de button_font dans run_single_player")
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
                print("FixedSetupScreen: Réinitialisation de button_font avant de dessiner le bouton")
                self.button_font = pygame.font.SysFont(None, 30)
            
            try:
                # Dessiner le bouton de démarrage avec gestion d'erreur
                self.start_button.draw(self.screen, self.button_font)
            except AttributeError as e:
                print(f"FixedSetupScreen: Erreur lors du dessin du bouton: {e}")
                # Si button_font n'est pas défini, le créer
                self.button_font = pygame.font.SysFont(None, 30)
                self.start_button.draw(self.screen, self.button_font)
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
        
        return None  # Si la boucle est interrompue

def fixed_setup_game(screen_width=900, screen_height=600, setup_complete_callback=None):
    """Version corrigée de la méthode setup_game qui utilise FixedSetupScreen.
    
    Args:
        screen_width: Largeur de l'écran
        screen_height: Hauteur de l'écran
        setup_complete_callback: Fonction à appeler lorsque la configuration est terminée
        
    Returns:
        Game: Instance du jeu configuré, ou None si l'utilisateur a annulé
    """
    print("DEBUG: fixed_setup_game from ui/setup_screen_fix.py is being called!")
    
    # Initialiser pygame si ce n'est pas déjà fait
    if not pygame.get_init():
        pygame.init()
    
    # Créer et exécuter l'écran de configuration des animaux
    setup_screen = FixedSetupScreen(screen_width, screen_height)
    
    # S'assurer que button_font est initialisé
    setup_screen.button_font = pygame.font.SysFont(None, 30)
    print("fixed_setup_game: button_font initialisé")
    
    # En mode multijoueur, on ne configure qu'un seul animal
    if setup_complete_callback:
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