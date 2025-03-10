import pygame
import sys
import os

# Initialisation de Pygame
pygame.init()

# Importer les paramètres de configuration
from game.config import (
    HP_CONVERSION, STAMINA_CONVERSION, SPEED_CONVERSION,
    TEETH_CONVERSION, CLAWS_CONVERSION, SKIN_CONVERSION, HEIGHT_CONVERSION,
    MAX_POINTS, 
    HP_MIN, HP_MAX, STAMINA_MIN, STAMINA_MAX, SPEED_MIN, SPEED_MAX,
    TEETH_MIN, TEETH_MAX, CLAWS_MIN, CLAWS_MAX, SKIN_MIN, SKIN_MAX,
    HEIGHT_MIN, HEIGHT_MAX,
    BITE_DAMAGE, SLAP_DAMAGE, SLAP_SPEED_GAIN, RUN_SPEED_GAIN,
    GREEN_FRUIT_POSITIONS, RED_FRUIT_POSITIONS, LION_START_POSITION, TIGER_START_POSITION,
    FRUIT_STAMINA_RECOVERY, FRUIT_HEAL_AMOUNT,
    GREEN_FRUIT_HEAL_AMOUNT, GREEN_FRUIT_STAMINA_RECOVERY,
    RED_FRUIT_HEAL_AMOUNT, RED_FRUIT_STAMINA_RECOVERY,
    SQUARE_SPEED, SQUARE_FRUIT_PROBABILITY,
    # Couleurs
    WHITE, BLACK, GRAY, LIGHT_GRAY, BLUE, RED, GREEN, YELLOW,
    DARK_BLUE, LIGHT_BLUE, DARK_RED, ORANGE, BROWN, LIGHT_RED, READY_RED,
    PURPLE,
    # Paramètres de récupération
    WATER_THIRST_RECOVERY,
    GREEN_FRUIT_HUNGER_RECOVERY,
    RED_FRUIT_HUNGER_RECOVERY,
    FRUIT_HUNGER_RECOVERY
)

from game.square import Square

# Tailles et dimensions
CELL_SIZE = 60
MARGIN = 5
INFO_WIDTH = 300
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 10

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, label, color=BLUE, step=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.color = color
        self.handle_radius = height * 1.5
        self.dragging = False
        self.step = step  # Pas d'incrémentation
        
    def draw(self, screen, font):
        # Dessiner la barre du slider
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, border_radius=self.rect.height // 2)
        
        # Calculer la position du curseur
        handle_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        handle_pos = (handle_x, self.rect.y + self.rect.height // 2)
        
        # Dessiner la partie remplie du slider
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(screen, self.color, filled_rect, border_radius=self.rect.height // 2)
        
        # Dessiner le curseur
        pygame.draw.circle(screen, self.color, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, BLACK, handle_pos, self.handle_radius, 2)
        
        # Dessiner le label et la valeur
        label_text = font.render(f"{self.label}: {self.value}", True, BLACK)
        label_rect = label_text.get_rect(midleft=(self.rect.x, self.rect.y - 20))
        screen.blit(label_text, label_rect)
    
    def is_handle_hovered(self, pos):
        handle_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        handle_pos = (handle_x, self.rect.y + self.rect.height // 2)
        distance = ((pos[0] - handle_pos[0]) ** 2 + (pos[1] - handle_pos[1]) ** 2) ** 0.5
        return distance <= self.handle_radius
    
    def update(self, pos):
        if self.dragging:
            # Limiter la position à l'intérieur du slider
            x = max(self.rect.x, min(pos[0], self.rect.x + self.rect.width))
            # Calculer la nouvelle valeur
            ratio = (x - self.rect.x) / self.rect.width
            raw_value = self.min_value + ratio * (self.max_value - self.min_value)
            
            # Arrondir au multiple du pas le plus proche
            if self.step > 1:
                self.value = int(round(raw_value / self.step) * self.step)
            else:
                self.value = int(raw_value)
            
            # S'assurer que la valeur est dans les limites
            self.value = max(self.min_value, min(self.value, self.max_value))
            
            return True
        return False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_handle_hovered(event.pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        return False
    
    def set_step(self, step):
        """Définit le pas d'incrémentation du slider"""
        self.step = step
        # Ajuster la valeur actuelle pour qu'elle soit un multiple du pas
        self.value = int(round(self.value / self.step) * self.step)

class SetupScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Configuration des Animaux")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Calculer les points minimums requis pour chaque animal
        min_points = (
            HP_MIN * HP_CONVERSION +
            STAMINA_MIN * STAMINA_CONVERSION +
            SPEED_MIN * SPEED_CONVERSION +
            TEETH_MIN * TEETH_CONVERSION +
            CLAWS_MIN * CLAWS_CONVERSION +
            SKIN_MIN * SKIN_CONVERSION +
            HEIGHT_MIN * HEIGHT_CONVERSION
        )
        
        # Points restants à distribuer après avoir satisfait les minimums
        remaining_points = MAX_POINTS - min_points
        
        # Paramètres par défaut pour les animaux pré-configurés
        # Chaque animal utilise exactement 100 points
        self.predefined_animals = {
            "Lion": {
                "hp": HP_MIN * HP_CONVERSION + 6,          # +3 HP
                "stamina": STAMINA_MIN * STAMINA_CONVERSION + 5,  # +5 stamina
                "speed": SPEED_MIN * SPEED_CONVERSION + 5,        # +1 speed
                "teeth": TEETH_MIN * TEETH_CONVERSION + 12,       # +4 teeth
                "claws": CLAWS_MIN * CLAWS_CONVERSION + 3,        # +1 claws
                "skin": SKIN_MIN * SKIN_CONVERSION + 3,           # +1 skin
                "height": HEIGHT_MIN * HEIGHT_CONVERSION + 10     # +10 height
            },
            "Tiger": {
                "hp": HP_MIN * HP_CONVERSION + 4,          # +2 HP
                "stamina": STAMINA_MIN * STAMINA_CONVERSION + 10, # +10 stamina
                "speed": SPEED_MIN * SPEED_CONVERSION + 10,       # +2 speed
                "teeth": TEETH_MIN * TEETH_CONVERSION + 3,        # +1 teeth
                "claws": CLAWS_MIN * CLAWS_CONVERSION + 12,       # +4 claws
                "skin": SKIN_MIN * SKIN_CONVERSION + 9,           # +3 skin
                "height": HEIGHT_MIN * HEIGHT_CONVERSION + 6      # +6 height
            }
        }
        
        # Vérifier que chaque animal utilise exactement 100 points
        lion_total = sum(self.predefined_animals["Lion"].values())
        tiger_total = sum(self.predefined_animals["Tiger"].values())
        
        # Ajuster si nécessaire (ne devrait pas être nécessaire si les calculs sont corrects)
        if lion_total != MAX_POINTS:
            # Ajuster la hauteur pour atteindre exactement 100 points
            self.predefined_animals["Lion"]["height"] += (MAX_POINTS - lion_total)
        
        if tiger_total != MAX_POINTS:
            # Ajuster la hauteur pour atteindre exactement 100 points
            self.predefined_animals["Tiger"]["height"] += (MAX_POINTS - tiger_total)
        
        # Paramètres pour les animaux des joueurs (tous au minimum)
        self.player1_animal_params = {
            "hp": HP_MIN * HP_CONVERSION,
            "stamina": STAMINA_MIN * STAMINA_CONVERSION,
            "speed": SPEED_MIN * SPEED_CONVERSION,
            "teeth": TEETH_MIN * TEETH_CONVERSION,
            "claws": CLAWS_MIN * CLAWS_CONVERSION,
            "skin": SKIN_MIN * SKIN_CONVERSION,
            "height": HEIGHT_MIN * HEIGHT_CONVERSION
        }
        
        self.player2_animal_params = {
            "hp": HP_MIN * HP_CONVERSION,
            "stamina": STAMINA_MIN * STAMINA_CONVERSION,
            "speed": SPEED_MIN * SPEED_CONVERSION,
            "teeth": TEETH_MIN * TEETH_CONVERSION,
            "claws": CLAWS_MIN * CLAWS_CONVERSION,
            "skin": SKIN_MIN * SKIN_CONVERSION,
            "height": HEIGHT_MIN * HEIGHT_CONVERSION
        }
        
        # Noms des animaux des joueurs
        self.player1_animal_name = "Animal Joueur 1"
        self.player2_animal_name = "Animal Joueur 2"
        
        # Phase de configuration (1 = joueur 1, 2 = joueur 2)
        self.current_phase = 1
        
        # État actuel de la configuration
        self.current_animal = "player"  # "player", "Lion", "Tiger"
        self.remaining_points = MAX_POINTS - sum(self.player1_animal_params.values())
        
        # Définir les dimensions et positions des éléments
        # Titre principal (en haut de l'écran)
        self.title_y = 20
        
        # Boutons pour les animaux pré-configurés
        self.predefined_button_width = 180
        self.predefined_button_height = 40
        self.predefined_button_y = 80
        
        # Espacer les boutons horizontalement
        button_spacing = 20
        total_width = 3 * self.predefined_button_width + 2 * button_spacing
        first_button_x = (screen_width - total_width) // 2
        
        self.use_lion_button = Button(
            first_button_x,
            self.predefined_button_y,
            self.predefined_button_width,
            self.predefined_button_height,
            "Utiliser Lion",
            YELLOW,
            (200, 200, 50)
        )
        
        self.use_tiger_button = Button(
            first_button_x + self.predefined_button_width + button_spacing,
            self.predefined_button_y,
            self.predefined_button_width,
            self.predefined_button_height,
            "Utiliser Tigre",
            ORANGE,
            (200, 100, 50)
        )
        
        self.use_custom_button = Button(
            first_button_x + 2 * (self.predefined_button_width + button_spacing),
            self.predefined_button_y,
            self.predefined_button_width,
            self.predefined_button_height,
            "Animal personnalisé",
            BLUE,
            (50, 50, 200)
        )
        
        # Champ de saisie du nom
        self.name_input_width = 300
        self.name_input_height = 40
        self.name_input_y = 140
        self.name_input_rect = pygame.Rect(
            (screen_width - self.name_input_width) // 2,
            self.name_input_y,
            self.name_input_width,
            self.name_input_height
        )
        self.name_input_active = False
        
        # Tableau des statistiques
        self.table_y = 200
        self.table_width = 600
        self.table_x = (screen_width - self.table_width) // 2
        
        # Bouton de navigation (en bas de l'écran)
        button_width = 200
        button_height = 40
        button_x = (screen_width - button_width) // 2
        button_y = screen_height - 60  # Toujours en bas de l'écran
        
        self.next_button = Button(button_x, button_y, button_width, button_height, "Joueur suivant", BLUE, (50, 50, 200))
        self.start_button = Button(button_x, button_y, button_width, button_height, "Commencer la partie", GREEN, (50, 200, 50))
        
        # Créer les boutons fléchés pour chaque statistique
        self.create_arrow_buttons()
        
        # Charger les images des animaux
        self.load_animal_images()
    
    def create_arrow_buttons(self):
        """Crée les boutons fléchés pour incrémenter/décrémenter les statistiques"""
        # Dimensions des boutons fléchés
        arrow_width = 30
        arrow_height = 30
        
        # Espacement entre les boutons et la barre
        button_margin = 10
        
        # Largeur de la barre de statistique
        bar_width = 300
        
        # Position de la barre (centrée dans le tableau)
        bar_x = self.table_x + 200  # Laisser de l'espace pour le nom de la statistique
        
        # Créer les dictionnaires pour stocker les boutons
        self.minus_buttons = {}
        self.plus_buttons = {}
        
        # Liste des statistiques
        stats = ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]
        
        # Hauteur de chaque ligne
        row_height = 40
        
        # Créer les boutons pour chaque statistique
        for i, stat in enumerate(stats):
            row_y = self.table_y + i * row_height
            
            # Bouton -
            minus_x = bar_x - button_margin - arrow_width
            minus_y = row_y + (row_height - arrow_height) // 2  # Centrer verticalement
            self.minus_buttons[stat] = Button(minus_x, minus_y, arrow_width, arrow_height, "-", 
                                             color=LIGHT_GRAY, hover_color=RED)
            
            # Bouton +
            plus_x = bar_x + bar_width + button_margin
            plus_y = row_y + (row_height - arrow_height) // 2  # Centrer verticalement
            self.plus_buttons[stat] = Button(plus_x, plus_y, arrow_width, arrow_height, "+", 
                                           color=LIGHT_GRAY, hover_color=GREEN)
        
        # Stocker la position et la largeur de la barre pour la méthode draw_table
        self.bar_x = bar_x
        self.bar_width = bar_width
    
    def load_animal_images(self):
        """Charge les images des animaux"""
        # Créer une surface pour le Lion
        lion_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Corps du Lion (cercle jaune)
        pygame.draw.circle(lion_img, YELLOW, (50, 50), 40)
        
        # Tête du Lion (cercle plus petit et plus foncé)
        pygame.draw.circle(lion_img, (200, 180, 0), (30, 30), 20)
        
        # Pattes du Lion (petits rectangles marron)
        pygame.draw.rect(lion_img, BROWN, (30, 80, 10, 20))
        pygame.draw.rect(lion_img, BROWN, (60, 80, 10, 20))
        pygame.draw.rect(lion_img, BROWN, (20, 60, 10, 20))
        pygame.draw.rect(lion_img, BROWN, (70, 60, 10, 20))
        
        # Créer une surface pour le Tigre
        tiger_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Corps du Tigre (cercle orange)
        pygame.draw.circle(tiger_img, ORANGE, (50, 50), 40)
        
        # Tête du Tigre (cercle plus petit et plus foncé)
        pygame.draw.circle(tiger_img, (200, 100, 0), (30, 30), 20)
        
        # Rayures du Tigre (lignes noires)
        for i in range(5):
            pygame.draw.line(tiger_img, BLACK, (30 + i * 10, 20), (30 + i * 10, 80), 3)
        
        # Pattes du Tigre (petits rectangles marron-orange)
        pygame.draw.rect(tiger_img, (150, 80, 0), (30, 80, 10, 20))
        pygame.draw.rect(tiger_img, (150, 80, 0), (60, 80, 10, 20))
        pygame.draw.rect(tiger_img, (150, 80, 0), (20, 60, 10, 20))
        pygame.draw.rect(tiger_img, (150, 80, 0), (70, 60, 10, 20))
        
        self.animal_images = {
            "Lion": lion_img,
            "Tiger": tiger_img
        }
    
    def update_remaining_points(self):
        """Met à jour le nombre de points restants"""
        if self.current_phase == 1:
            if self.current_animal == "player":
                self.remaining_points = MAX_POINTS - sum(self.player1_animal_params.values())
            else:
                self.remaining_points = MAX_POINTS - sum(self.predefined_animals[self.current_animal].values())
        else:  # Phase 2
            if self.current_animal == "player":
                self.remaining_points = MAX_POINTS - sum(self.player2_animal_params.values())
            else:
                self.remaining_points = MAX_POINTS - sum(self.predefined_animals[self.current_animal].values())
    
    def handle_stat_change(self, stat, change):
        """Gère le changement d'une statistique
        
        Args:
            stat: La statistique à modifier (hp, stamina, speed)
            change: La valeur du changement (+1 ou -1)
        """
        # Sélectionner les paramètres en fonction de la phase et de l'animal actuel
        if self.current_phase == 1:
            params = self.player1_animal_params if self.current_animal == "player" else self.predefined_animals[self.current_animal]
        else:  # Phase 2
            params = self.player2_animal_params if self.current_animal == "player" else self.predefined_animals[self.current_animal]
        
        # Calculer la nouvelle valeur en points bruts
        new_value = params[stat] + change
        
        # Définir les limites et conversions pour chaque statistique
        stat_config = {
            "hp": {"min": HP_MIN, "max": HP_MAX, "conversion": HP_CONVERSION},
            "stamina": {"min": STAMINA_MIN, "max": STAMINA_MAX, "conversion": STAMINA_CONVERSION},
            "speed": {"min": SPEED_MIN, "max": SPEED_MAX, "conversion": SPEED_CONVERSION},
            "teeth": {"min": TEETH_MIN, "max": TEETH_MAX, "conversion": TEETH_CONVERSION},
            "claws": {"min": CLAWS_MIN, "max": CLAWS_MAX, "conversion": CLAWS_CONVERSION},
            "skin": {"min": SKIN_MIN, "max": SKIN_MAX, "conversion": SKIN_CONVERSION},
            "height": {"min": HEIGHT_MIN, "max": HEIGHT_MAX, "conversion": HEIGHT_CONVERSION}
        }
        
        # Récupérer la configuration pour la statistique actuelle
        config = stat_config[stat]
        
        # Calculer la valeur convertie (valeur réelle de la caractéristique)
        converted_value = new_value // config["conversion"]
        
        # Vérifier si la valeur convertie est valide
        if converted_value < config["min"]:
            return False
        if converted_value > config["max"]:
            return False
        
        # Vérifier si le joueur a assez de points
        if change > 0 and self.remaining_points < change:
            return False
        
        # Appliquer le changement
        params[stat] = new_value
        
        # Mettre à jour le nombre de points restants
        self.update_remaining_points()
        
        return True
    
    def draw_table(self):
        """Dessine le tableau des statistiques"""
        # Effacer l'écran
        self.screen.fill(WHITE)
        
        # Récupérer les paramètres de l'animal actuel en fonction de la phase
        if self.current_phase == 1:
            params = self.player1_animal_params if self.current_animal == "player" else self.predefined_animals[self.current_animal]
            current_name = self.player1_animal_name
        else:  # Phase 2
            params = self.player2_animal_params if self.current_animal == "player" else self.predefined_animals[self.current_animal]
            current_name = self.player2_animal_name
        
        # Dessiner le titre principal
        phase_text = f"Configuration de l'animal - Joueur {self.current_phase}"
        title_text = self.title_font.render(phase_text, True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.title_y + self.title_font.get_height() // 2))
        self.screen.blit(title_text, title_rect)
        
        # Dessiner les boutons pour les animaux pré-configurés
        self.use_lion_button.draw(self.screen, self.small_font)
        self.use_tiger_button.draw(self.screen, self.small_font)
        self.use_custom_button.draw(self.screen, self.small_font)
        
        # Dessiner l'image de l'animal actuel si disponible
        if self.current_animal in self.animal_images:
            animal_img = self.animal_images[self.current_animal]
            img_rect = animal_img.get_rect(center=(self.screen_width // 2, self.name_input_y - 20))
            self.screen.blit(animal_img, img_rect)
        
        # Dessiner le champ de saisie du nom de l'animal
        name_label = self.font.render("Nom de votre animal:", True, BLACK)
        name_label_rect = name_label.get_rect(right=self.name_input_rect.left - 10, centery=self.name_input_rect.centery)
        self.screen.blit(name_label, name_label_rect)
        
        # Dessiner le champ de saisie
        pygame.draw.rect(self.screen, WHITE, self.name_input_rect)
        pygame.draw.rect(self.screen, BLACK if self.name_input_active else GRAY, self.name_input_rect, 2)
        
        # Afficher le nom de l'animal actuel
        if self.current_phase == 1:
            name_text = self.font.render(self.player1_animal_name, True, BLACK)
        else:
            name_text = self.font.render(self.player2_animal_name, True, BLACK)
        name_text_rect = name_text.get_rect(left=self.name_input_rect.left + 10, centery=self.name_input_rect.centery)
        self.screen.blit(name_text, name_text_rect)
        
        # Dessiner le titre du tableau des statistiques
        if self.current_animal == "player":
            stats_title = self.font.render(f"Statistiques de {current_name}", True, BLACK)
        else:
            stats_title = self.font.render(f"Statistiques du {self.current_animal}", True, BLACK)
        stats_title_rect = stats_title.get_rect(left=self.table_x, top=self.table_y - 40)
        self.screen.blit(stats_title, stats_title_rect)
        
        # Dessiner les points restants
        remaining_text = self.font.render(f"Points restants: {self.remaining_points}", True, 
                                         GREEN if self.remaining_points >= 0 else RED)
        remaining_rect = remaining_text.get_rect(right=self.table_x + self.table_width, top=self.table_y - 40)
        self.screen.blit(remaining_text, remaining_rect)
        
        # Définir les statistiques et leurs couleurs avec leurs limites spécifiques
        stats = [
            {"name": "Points de vie (HP)", "key": "hp", "color": RED, "conversion": HP_CONVERSION, "min": HP_MIN, "max": HP_MAX},
            {"name": "Endurance (Stamina)", "key": "stamina", "color": BLUE, "conversion": STAMINA_CONVERSION, "min": STAMINA_MIN, "max": STAMINA_MAX},
            {"name": "Vitesse (Speed)", "key": "speed", "color": GREEN, "conversion": SPEED_CONVERSION, "min": SPEED_MIN, "max": SPEED_MAX},
            {"name": "Dents (Teeth)", "key": "teeth", "color": YELLOW, "conversion": TEETH_CONVERSION, "min": TEETH_MIN, "max": TEETH_MAX},
            {"name": "Griffes (Claws)", "key": "claws", "color": ORANGE, "conversion": CLAWS_CONVERSION, "min": CLAWS_MIN, "max": CLAWS_MAX},
            {"name": "Peau (Skin)", "key": "skin", "color": BROWN, "conversion": SKIN_CONVERSION, "min": SKIN_MIN, "max": SKIN_MAX},
            {"name": "Taille (Height)", "key": "height", "color": DARK_BLUE, "conversion": HEIGHT_CONVERSION, "min": HEIGHT_MIN, "max": HEIGHT_MAX}
        ]
        
        # Dessiner chaque ligne du tableau
        row_height = 40
        for i, stat_info in enumerate(stats):
            y = self.table_y + i * row_height
            stat_key = stat_info["key"]
            
            # Nom de la statistique
            stat_text = self.small_font.render(stat_info["name"], True, BLACK)
            stat_text_rect = stat_text.get_rect(left=self.table_x, centery=y + row_height // 2)
            self.screen.blit(stat_text, stat_text_rect)
            
            # Valeur de la statistique (points bruts et valeur convertie)
            raw_value = params[stat_key]
            converted_value = raw_value // stat_info["conversion"]
            value_text = self.small_font.render(f"{raw_value} ({converted_value})", True, BLACK)
            
            # Récupérer les positions des boutons
            minus_button = self.minus_buttons[stat_key]
            plus_button = self.plus_buttons[stat_key]
            
            # Utiliser les positions de barre stockées dans create_arrow_buttons
            bar_x = self.bar_x
            bar_width = self.bar_width
            bar_y = y + (row_height - 30) // 2  # Centrer verticalement
            bar_height = 30
            
            # Dessiner la barre de fond
            pygame.draw.rect(self.screen, LIGHT_GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Dessiner la barre de valeur basée sur la valeur convertie
            # La barre est vide à 0 et pleine au maximum
            min_val = 0  # Toujours commencer à 0 pour une barre vide
            max_val = stat_info["max"]  # Utiliser la valeur maximale spécifique à chaque stat
            
            # Calculer la largeur de la barre proportionnellement à la valeur convertie
            if max_val > min_val:
                value_width = int(bar_width * (converted_value - min_val) / (max_val - min_val))
            else:
                value_width = 0
                
            # S'assurer que la barre a une largeur minimale de 0 (pas de coloration si value <= 0)
            value_width = max(0, value_width)
            # S'assurer que la barre ne dépasse pas la largeur maximale
            value_width = min(bar_width, value_width)
            
            pygame.draw.rect(self.screen, stat_info["color"], (bar_x, bar_y, value_width, bar_height))
            
            # Dessiner le contour de la barre
            pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Dessiner les boutons + et -
            minus_button.draw(self.screen, self.small_font)
            plus_button.draw(self.screen, self.small_font)
            
            # Afficher la valeur au centre de la barre
            value_text_rect = value_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            self.screen.blit(value_text, value_text_rect)
        
        # Dessiner le bouton de confirmation en bas du tableau
        if self.current_phase == 1:
            self.next_button.draw(self.screen, self.font)
        else:
            self.start_button.draw(self.screen, self.font)
    
    def run(self):
        """Exécute l'écran de configuration"""
        running = True
        
        while running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None  # Quitter sans démarrer le jeu
                
                # Gérer les clics sur les boutons
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    
                    # Vérifier si le clic est sur le champ de saisie du nom
                    if self.name_input_rect.collidepoint(mouse_pos):
                        self.name_input_active = not self.name_input_active
                    else:
                        self.name_input_active = False
                    
                    # Boutons pour les animaux pré-configurés
                    if self.use_lion_button.is_hovered(mouse_pos):
                        self.current_animal = "Lion"
                        self.update_remaining_points()
                    elif self.use_tiger_button.is_hovered(mouse_pos):
                        self.current_animal = "Tiger"
                        self.update_remaining_points()
                    elif self.use_custom_button.is_hovered(mouse_pos):
                        self.current_animal = "player"
                        self.update_remaining_points()
                    
                    # Bouton de navigation (suivant ou démarrer)
                    if self.current_phase == 1 and self.next_button.is_hovered(mouse_pos):
                        # Sauvegarder les paramètres du joueur 1 et passer au joueur 2
                        if self.current_animal == "player":
                            self.player1_params = {"name": self.player1_animal_name, "params": self.player1_animal_params.copy()}
                        else:
                            self.player1_params = {"name": self.current_animal, "params": self.predefined_animals[self.current_animal].copy()}
                        
                        # Passer à la phase 2
                        self.current_phase = 2
                        self.current_animal = "player"
                        self.update_remaining_points()
                        
                    elif self.current_phase == 2 and self.start_button.is_hovered(mouse_pos):
                        # Sauvegarder les paramètres du joueur 2 et démarrer le jeu
                        if self.current_animal == "player":
                            self.player2_params = {"name": self.player2_animal_name, "params": self.player2_animal_params.copy()}
                        else:
                            self.player2_params = {"name": self.current_animal, "params": self.predefined_animals[self.current_animal].copy()}
                        
                        # Retourner les paramètres des deux joueurs
                        return self.player1_params, self.player2_params
                    
                    # Boutons d'incrémentation/décrémentation (seulement pour l'animal personnalisé)
                    if self.current_animal == "player":
                        for stat in ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]:
                            if self.minus_buttons[stat].is_hovered(mouse_pos):
                                self.handle_stat_change(stat, -1)
                            elif self.plus_buttons[stat].is_hovered(mouse_pos):
                                self.handle_stat_change(stat, 1)
                
                # Gérer la saisie du nom
                if event.type == pygame.KEYDOWN:
                    if self.name_input_active:
                        if event.key == pygame.K_RETURN:
                            self.name_input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            if self.current_phase == 1:
                                self.player1_animal_name = self.player1_animal_name[:-1]
                            else:
                                self.player2_animal_name = self.player2_animal_name[:-1]
                        else:
                            # Limiter la longueur du nom à 20 caractères
                            if self.current_phase == 1 and len(self.player1_animal_name) < 20:
                                self.player1_animal_name += event.unicode
                            elif self.current_phase == 2 and len(self.player2_animal_name) < 20:
                                self.player2_animal_name += event.unicode
            
            # Mettre à jour les boutons
            mouse_pos = pygame.mouse.get_pos()
            
            # Boutons de navigation
            if self.current_phase == 1:
                self.next_button.update(mouse_pos)
            else:
                self.start_button.update(mouse_pos)
            
            # Boutons pour les animaux pré-configurés
            self.use_lion_button.update(mouse_pos)
            self.use_tiger_button.update(mouse_pos)
            self.use_custom_button.update(mouse_pos)
            
            # Boutons d'incrémentation/décrémentation
            for stat in ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]:
                self.minus_buttons[stat].update(mouse_pos)
                self.plus_buttons[stat].update(mouse_pos)
                
                # Désactiver les boutons +/- si on n'est pas sur l'animal personnalisé
                self.minus_buttons[stat].active = (self.current_animal == "player")
                self.plus_buttons[stat].active = (self.current_animal == "player")
            
            # Dessiner l'écran
            self.screen.fill(WHITE)
            self.draw_table()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
        
        return None, None  # Si la boucle est interrompue

    def run_single_player(self):
        """Exécute l'écran de configuration pour un seul joueur (mode multijoueur)"""
        running = True
        
        while running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Quitter sans démarrer le jeu
                
                # Gérer les clics sur les boutons
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    
                    # Vérifier si le clic est sur le champ de saisie du nom
                    if self.name_input_rect.collidepoint(mouse_pos):
                        self.name_input_active = not self.name_input_active
                    else:
                        self.name_input_active = False
                    
                    # Boutons pour les animaux pré-configurés
                    if self.use_lion_button.is_hovered(mouse_pos):
                        self.current_animal = "Lion"
                        self.update_remaining_points()
                    elif self.use_tiger_button.is_hovered(mouse_pos):
                        self.current_animal = "Tiger"
                        self.update_remaining_points()
                    elif self.use_custom_button.is_hovered(mouse_pos):
                        self.current_animal = "player"
                        self.update_remaining_points()
                    
                    # Bouton de démarrage
                    if self.start_button.is_hovered(mouse_pos):
                        # Sauvegarder les paramètres du joueur et démarrer le jeu
                        if self.current_animal == "player":
                            return {"name": self.player1_animal_name, "params": self.player1_animal_params.copy()}
                        else:
                            return {"name": self.current_animal, "params": self.predefined_animals[self.current_animal].copy()}
                    
                    # Boutons d'incrémentation/décrémentation (seulement pour l'animal personnalisé)
                    if self.current_animal == "player":
                        for stat in ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]:
                            if self.minus_buttons[stat].is_hovered(mouse_pos):
                                self.handle_stat_change(stat, -1)
                            elif self.plus_buttons[stat].is_hovered(mouse_pos):
                                self.handle_stat_change(stat, 1)
                
                # Gérer la saisie du nom
                if event.type == pygame.KEYDOWN:
                    if self.name_input_active:
                        if event.key == pygame.K_RETURN:
                            self.name_input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.player1_animal_name = self.player1_animal_name[:-1]
                        else:
                            # Limiter la longueur du nom à 20 caractères
                            if len(self.player1_animal_name) < 20:
                                self.player1_animal_name += event.unicode
            
            # Mettre à jour les boutons
            mouse_pos = pygame.mouse.get_pos()
            
            # Bouton de démarrage
            self.start_button.update(mouse_pos)
            
            # Boutons pour les animaux pré-configurés
            self.use_lion_button.update(mouse_pos)
            self.use_tiger_button.update(mouse_pos)
            self.use_custom_button.update(mouse_pos)
            
            # Boutons d'incrémentation/décrémentation
            for stat in ["hp", "stamina", "speed", "teeth", "claws", "skin", "height"]:
                self.minus_buttons[stat].update(mouse_pos)
                self.plus_buttons[stat].update(mouse_pos)
                
                # Désactiver les boutons +/- si on n'est pas sur l'animal personnalisé
                self.minus_buttons[stat].active = (self.current_animal == "player")
                self.plus_buttons[stat].active = (self.current_animal == "player")
            
            # Dessiner l'écran
            self.screen.fill(WHITE)
            
            # Dessiner le titre
            title = self.title_font.render("Configuration de votre animal", True, BLACK)
            title_rect = title.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(title, title_rect)
            
            # Dessiner le tableau de configuration
            self.draw_table()
            
            # Dessiner le bouton de démarrage
            self.start_button.draw(self.screen, self.button_font)
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
        
        return None  # Si la boucle est interrompue

class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, hover_color=BLUE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.active = True
    
    def draw(self, screen, font):
        # Dessiner le bouton
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        # Dessiner le texte
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos) and self.active
    
    def update(self, pos):
        if self.is_hovered(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

class GUI:
    def __init__(self, game):
        self.game = game
        self.terrain = game.terrain
        
        # Initialiser pygame
        pygame.init()
        
        # Calculer la taille de la fenêtre
        self.width = self.terrain.width * CELL_SIZE + INFO_WIDTH
        self.height = self.terrain.height * CELL_SIZE + 80  # Ajouter de l'espace pour la barre de vitesse
        
        # Créer la fenêtre
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Jeu des Animaux")
        
        # Initialiser les polices
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Initialiser les variables de jeu
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_animal = self.game.get_next_animal_to_play()
        self.selected_animal = None
        self.selected_action = None
        self.highlighted_cells = []
        self.highlighted_animals = []
        
        # Variables pour l'animation
        self.animation_in_progress = False
        self.animating_animal = None
        self.animation_start_pos = None
        self.animation_end_pos = None
        self.animation_frames = 30  # Nombre de frames pour l'animation
        self.animation_current_frame = 0
        
        # Variables pour les messages d'information
        self.info_message = None
        self.info_message_timer = 0
        
        # Charger les images
        self.load_images()
        
        # Mettre à jour les cellules et animaux ciblables
        if self.current_animal:
            self.selected_animal = self.current_animal
            self.update_highlights()
    
    @staticmethod
    def setup_game(screen_width=900, screen_height=600, setup_complete_callback=None):
        """Affiche l'écran de configuration et crée un nouveau jeu avec les paramètres choisis
        
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
        setup_screen = SetupScreen(screen_width, screen_height)
        
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
        player_params = player_data["params"]
        
        # En mode multijoueur (avec callback), ne créer que l'animal du joueur
        if setup_complete_callback:
            # Déterminer la position de départ en fonction de l'ID du joueur
            # (sera mis à jour lors de la synchronisation)
            position = LION_START_POSITION
            
            # Créer l'animal du joueur
            player_animal = Animal(
                player_name, 
                hp=player_params["hp"] // HP_CONVERSION, 
                stamina=player_params["stamina"] // STAMINA_CONVERSION, 
                speed=player_params["speed"] // SPEED_CONVERSION, 
                position=position,
                teeth=player_params["teeth"] // TEETH_CONVERSION,
                claws=player_params["claws"] // CLAWS_CONVERSION,
                skin=player_params["skin"] // SKIN_CONVERSION,
                height=player_params["height"] // HEIGHT_CONVERSION
            )
            
            # Ajouter l'animal au jeu
            game.add_animal(player_animal, position)
            
            # Ajouter quelques fruits
            for pos in GREEN_FRUIT_POSITIONS:
                fruit = GreenFruit(position=pos)
                game.add_resource(fruit, pos)
            
            for pos in RED_FRUIT_POSITIONS:
                fruit = RedFruit(position=pos)
                game.add_resource(fruit, pos)
            
            # Appeler le callback pour signaler que la configuration est terminée
            if setup_complete_callback:
                setup_complete_callback(game)
            
            return game
        
        # En mode solo, créer les deux animaux
        else:
            opponent_name = opponent_data["name"]
            opponent_params = opponent_data["params"]
            
            # Créer les animaux avec les paramètres choisis et les conversions
            player_animal = Animal(
                player_name, 
                hp=player_params["hp"] // HP_CONVERSION, 
                stamina=player_params["stamina"] // STAMINA_CONVERSION, 
                speed=player_params["speed"] // SPEED_CONVERSION, 
                position=LION_START_POSITION,
                teeth=player_params["teeth"] // TEETH_CONVERSION,
                claws=player_params["claws"] // CLAWS_CONVERSION,
                skin=player_params["skin"] // SKIN_CONVERSION,
                height=player_params["height"] // HEIGHT_CONVERSION
            )
            
            opponent_animal = Animal(
                opponent_name, 
                hp=opponent_params["hp"] // HP_CONVERSION, 
                stamina=opponent_params["stamina"] // STAMINA_CONVERSION, 
                speed=opponent_params["speed"] // SPEED_CONVERSION, 
                position=TIGER_START_POSITION,
                teeth=opponent_params["teeth"] // TEETH_CONVERSION,
                claws=opponent_params["claws"] // CLAWS_CONVERSION,
                skin=opponent_params["skin"] // SKIN_CONVERSION,
                height=opponent_params["height"] // HEIGHT_CONVERSION
            )
            
            # Ajouter les animaux au jeu
            game.add_animal(player_animal, LION_START_POSITION)
            game.add_animal(opponent_animal, TIGER_START_POSITION)
            
            # Ajouter quelques fruits
            for pos in GREEN_FRUIT_POSITIONS:
                fruit = GreenFruit(position=pos)
                game.add_resource(fruit, pos)
            
            for pos in RED_FRUIT_POSITIONS:
                fruit = RedFruit(position=pos)
                game.add_resource(fruit, pos)
            
            return game
    
    def run(self):
        """Exécute la boucle principale du jeu"""
        # Initialiser l'animal actuel
        self.current_animal = self.game.get_next_animal_to_play()
        if self.current_animal:
            self.selected_animal = self.current_animal
            self.update_highlights()
            
        # Compteur de frames pour les mises à jour périodiques
        frame_count = 0
            
        while self.running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Vérifier si Shift est enfoncé
                    shift_pressed = pygame.key.get_mods() & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)
                    # Gérer les clics de souris
                    self.handle_click(event.pos, shift_pressed)
                elif event.type == pygame.MOUSEMOTION:
                    # Mettre à jour les boutons au survol (plus nécessaire, mais gardé pour compatibilité)
                    self.update_buttons(event.pos)
            
            # Mettre à jour l'animation si nécessaire
            if self.animation_in_progress:
                self.update_animation()
            
            # Incrémenter le compteur de frames
            frame_count += 1
            
            # Mettre à jour l'animal actuel si nécessaire
            if not self.animation_in_progress:  # Ne pas changer d'animal pendant une animation
                previous_animal = self.current_animal
                self.current_animal = self.game.get_next_animal_to_play()
                
                # Si un nouvel animal est prêt à jouer, le sélectionner automatiquement
                if self.current_animal and self.current_animal != previous_animal:
                    self.selected_animal = self.current_animal
                    self.show_info_message(f"C'est au tour de {self.current_animal.name}")
                    self.update_highlights()
            
            # Décrémenter le timer du message d'information
            if self.info_message_timer > 0:
                self.info_message_timer -= 1
            
            # Dessiner l'écran
            self.draw_terrain()
            self.draw_info_panel()
            
            # Dessiner la barre de vitesse
            self.draw_speed_bar()
            
            # Mettre à jour l'écran
            pygame.display.flip()
            
            # Limiter à 60 FPS
            self.clock.tick(60)
        
        pygame.quit()

    def load_images(self):
        """Charge les images pour les animaux et les ressources"""
        # Créer des surfaces pour les images
        self.images = {}
        
        # Image pour le Lion (corps jaune, tête plus foncée, pattes marron)
        lion_img = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        # Corps (cercle jaune)
        body_radius = (CELL_SIZE - 20) // 2
        body_center = (lion_img.get_width() // 2, lion_img.get_height() // 2)
        pygame.draw.circle(lion_img, (255, 220, 100), body_center, body_radius)
        # Tête (cercle plus petit et plus foncé)
        head_radius = body_radius // 2
        head_center = (body_center[0] - body_radius // 2, body_center[1] - body_radius // 2)
        pygame.draw.circle(lion_img, (230, 190, 80), head_center, head_radius)
        # Pattes (petits rectangles marron)
        leg_width, leg_height = body_radius // 3, body_radius // 2
        # Patte avant gauche
        pygame.draw.rect(lion_img, (150, 100, 50), 
                         (body_center[0] - body_radius + leg_width, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte avant droite
        pygame.draw.rect(lion_img, (150, 100, 50), 
                         (body_center[0] - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière gauche
        pygame.draw.rect(lion_img, (150, 100, 50), 
                         (body_center[0] + body_radius - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière droite
        pygame.draw.rect(lion_img, (150, 100, 50), 
                         (body_center[0] + body_radius - leg_width * 4, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        self.images["Lion"] = lion_img
        
        # Image pour le Tigre (corps orange avec des rayures noires)
        tiger_img = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        # Corps (cercle orange)
        pygame.draw.circle(tiger_img, (255, 165, 0), body_center, body_radius)
        # Tête (cercle plus petit et plus foncé)
        pygame.draw.circle(tiger_img, (220, 140, 0), head_center, head_radius)
        # Rayures (lignes noires)
        for i in range(3):
            offset = i * body_radius // 2
            pygame.draw.line(tiger_img, BLACK, 
                            (body_center[0] - body_radius // 2 + offset, body_center[1] - body_radius // 2),
                            (body_center[0] - body_radius // 2 + offset, body_center[1] + body_radius // 2),
                            2)
        # Pattes (petits rectangles marron foncé)
        # Patte avant gauche
        pygame.draw.rect(tiger_img, (120, 80, 40), 
                         (body_center[0] - body_radius + leg_width, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte avant droite
        pygame.draw.rect(tiger_img, (120, 80, 40), 
                         (body_center[0] - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière gauche
        pygame.draw.rect(tiger_img, (120, 80, 40), 
                         (body_center[0] + body_radius - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière droite
        pygame.draw.rect(tiger_img, (120, 80, 40), 
                         (body_center[0] + body_radius - leg_width * 4, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        self.images["Tiger"] = tiger_img
        
        # Image par défaut pour l'animal personnalisé du joueur (corps bleu)
        player_img = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        # Corps (cercle bleu)
        pygame.draw.circle(player_img, (100, 150, 255), body_center, body_radius)
        # Tête (cercle plus petit et plus foncé)
        pygame.draw.circle(player_img, (80, 120, 220), head_center, head_radius)
        # Pattes (petits rectangles gris)
        # Patte avant gauche
        pygame.draw.rect(player_img, (100, 100, 100), 
                         (body_center[0] - body_radius + leg_width, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte avant droite
        pygame.draw.rect(player_img, (100, 100, 100), 
                         (body_center[0] - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière gauche
        pygame.draw.rect(player_img, (100, 100, 100), 
                         (body_center[0] + body_radius - leg_width * 2, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Patte arrière droite
        pygame.draw.rect(player_img, (100, 100, 100), 
                         (body_center[0] + body_radius - leg_width * 4, 
                          body_center[1] + body_radius - leg_height // 2, 
                          leg_width, leg_height))
        # Ajouter cette image comme image par défaut
        self.images["default"] = player_img
        
        # Image pour le Fruit (cercle rouge avec tige verte)
        fruit_img = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20), pygame.SRCALPHA)
        # Corps du fruit (cercle rouge)
        pygame.draw.circle(fruit_img, (255, 50, 50), (fruit_img.get_width() // 2, fruit_img.get_height() // 2 + 5), (CELL_SIZE - 30) // 2)
        # Tige (rectangle vert)
        pygame.draw.rect(fruit_img, (50, 150, 50), (fruit_img.get_width() // 2 - 2, 5, 4, 10))
        # Feuille (petit cercle vert)
        pygame.draw.circle(fruit_img, (50, 200, 50), (fruit_img.get_width() // 2 + 5, 10), 5)
        self.images["Fruit"] = fruit_img
        
        # Image pour le Fruit Vert (cercle vert avec tige marron)
        green_fruit_img = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20), pygame.SRCALPHA)
        # Corps du fruit (cercle vert)
        pygame.draw.circle(green_fruit_img, (50, 200, 50), (green_fruit_img.get_width() // 2, green_fruit_img.get_height() // 2 + 5), (CELL_SIZE - 30) // 2)
        # Tige (rectangle marron)
        pygame.draw.rect(green_fruit_img, (139, 69, 19), (green_fruit_img.get_width() // 2 - 2, 5, 4, 10))
        # Feuille (petit cercle vert clair)
        pygame.draw.circle(green_fruit_img, (100, 255, 100), (green_fruit_img.get_width() // 2 + 5, 10), 5)
        # Ajouter un symbole "+" pour indiquer la régénération de HP
        hp_font = pygame.font.SysFont(None, 20)
        hp_text = hp_font.render("+", True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(green_fruit_img.get_width() // 2, green_fruit_img.get_height() // 2 + 5))
        green_fruit_img.blit(hp_text, text_rect)
        self.images["GreenFruit"] = green_fruit_img
        
        # Image pour le Fruit Rouge (cercle rouge avec tige verte)
        red_fruit_img = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20), pygame.SRCALPHA)
        # Corps du fruit (cercle rouge)
        pygame.draw.circle(red_fruit_img, (255, 50, 50), (red_fruit_img.get_width() // 2, red_fruit_img.get_height() // 2 + 5), (CELL_SIZE - 30) // 2)
        # Tige (rectangle vert)
        pygame.draw.rect(red_fruit_img, (50, 150, 50), (red_fruit_img.get_width() // 2 - 2, 5, 4, 10))
        # Feuille (petit cercle vert)
        pygame.draw.circle(red_fruit_img, (50, 200, 50), (red_fruit_img.get_width() // 2 + 5, 10), 5)
        # Ajouter un symbole "S" pour indiquer la régénération de Stamina
        stamina_font = pygame.font.SysFont(None, 20)
        stamina_text = stamina_font.render("S", True, (255, 255, 255))
        text_rect = stamina_text.get_rect(center=(red_fruit_img.get_width() // 2, red_fruit_img.get_height() // 2 + 5))
        red_fruit_img.blit(stamina_text, text_rect)
        self.images["RedFruit"] = red_fruit_img

    def draw_terrain(self):
        # Dessiner le fond du terrain
        self.screen.fill(WHITE)
        
        # PREMIÈRE PASSE : Dessiner la grille, les cases et les ressources
        for y in range(self.terrain.height):
            for x in range(self.terrain.width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                position = self.terrain.coordinates_to_position(x, y)
                square = self.terrain.get_square(position)
                
                # Déterminer la couleur de la case
                cell_color = WHITE
                
                # Si la case est une tuile d'eau, lui donner un fond bleu
                if square and square.terrain_type == Square.TYPE_WATER:
                    cell_color = (100, 150, 255)  # Bleu pour l'eau
                # Si la case est un verger (peut produire des fruits), lui donner un fond légèrement rouge
                elif square and square.is_orchard:
                    # Si la case a atteint 100 points de vitesse, utiliser une couleur plus vive
                    if square.speed_points >= 100:
                        cell_color = READY_RED
                    else:
                        cell_color = LIGHT_RED
                
                # Si un animal est sélectionné et que c'est son tour, montrer les déplacements possibles
                if self.selected_animal and self.selected_animal == self.current_animal:
                    actions = self.game.get_animal_possible_actions(self.selected_animal)
                    
                    # Colorer les cases accessibles pour marcher
                    if "walk" in actions and position in actions["walk"]:
                        cell_color = (180, 180, 255)  # Bleu clair pour "walk"
                    
                    # Les cases accessibles pour courir sont les mêmes que pour marcher
                    # puisque run ne déplace que d'une case maintenant
                
                # Dessiner la case
                pygame.draw.rect(self.screen, cell_color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                
                # Dessiner les ressources (mais pas les animaux)
                resource = self.terrain.get_resource_at(position)
                if resource:
                    # Dessiner l'image de la ressource
                    resource_img = self.images[resource.name]
                    img_rect = resource_img.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
                    self.screen.blit(resource_img, img_rect)
        
        # DEUXIÈME PASSE : Dessiner tous les animaux et leurs barres de vie
        for y in range(self.terrain.height):
            for x in range(self.terrain.width):
                position = self.terrain.coordinates_to_position(x, y)
                animal = self.terrain.get_animal_at(position)
                
                if animal and (not self.animation_in_progress or animal != self.animating_animal):
                    # Calculer le centre de la cellule
                    cell_center_x = x * CELL_SIZE + CELL_SIZE // 2
                    cell_center_y = y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Dessiner l'image de l'animal
                    # Utiliser l'image par défaut si l'animal n'a pas d'image spécifique
                    if animal.name in self.images:
                        animal_img = self.images[animal.name]
                    else:
                        animal_img = self.images["default"]
                    img_rect = animal_img.get_rect(center=(cell_center_x, cell_center_y))
                    self.screen.blit(animal_img, img_rect)
                    
                    # Calculer les coordonnées pour la tête et le corps
                    body_radius = (CELL_SIZE - 20) // 2
                    body_center = (cell_center_x, cell_center_y)
                    head_radius = body_radius // 2
                    head_center = (body_center[0] - body_radius // 2, body_center[1] - body_radius // 2)
                    
                    # Si l'animal est sélectionné, dessiner un contour
                    if animal == self.selected_animal:
                        pygame.draw.circle(self.screen, (0, 255, 0), body_center, body_radius + 2, 2)
                    
                    # Si l'animal peut être attaqué, mettre en évidence
                    if self.selected_animal and animal != self.selected_animal and self.selected_animal == self.current_animal:
                        actions = self.game.get_animal_possible_actions(self.selected_animal)
                        
                        # Mettre en évidence l'animal si on peut l'attaquer
                        if ("bite" in actions and animal in actions["bite"]) or ("slap" in actions and animal in actions["slap"]):
                            pygame.draw.circle(self.screen, RED, body_center, body_radius + 2, 2)
                    
                    # Dessiner les barres de vie et de stamina
                    bar_width = CELL_SIZE - 10  # Barres plus longues
                    bar_height = 10
                    bar_x = x * CELL_SIZE + 5  # Commencer plus à gauche
                    
                    # Barre de vie (verte) - positionnée 6 pixels plus bas
                    hp_bar_y = y * CELL_SIZE + CELL_SIZE - 19  # -25 + 6 = -19
                    hp_ratio = animal.hp / animal.max_hp
                    
                    # Dessiner une petite icône de cœur pour la vie
                    heart_size = 8
                    heart_x = bar_x - heart_size - 2
                    heart_y = hp_bar_y + bar_height // 2 - heart_size // 2
                    
                    # Dessiner un cœur rouge
                    pygame.draw.circle(self.screen, (255, 0, 0), (heart_x + heart_size // 3, heart_y + heart_size // 3), heart_size // 3)
                    pygame.draw.circle(self.screen, (255, 0, 0), (heart_x + heart_size - heart_size // 3, heart_y + heart_size // 3), heart_size // 3)
                    pygame.draw.polygon(self.screen, (255, 0, 0), [
                        (heart_x, heart_y + heart_size // 3),
                        (heart_x + heart_size, heart_y + heart_size // 3),
                        (heart_x + heart_size // 2, heart_y + heart_size)
                    ])
                    
                    # Fond de la barre (gris)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (bar_x, hp_bar_y, bar_width, bar_height))
                    # Barre de vie (verte)
                    hp_bar_width = max(int(bar_width * hp_ratio), 1)  # Au moins 1 pixel de large
                    pygame.draw.rect(self.screen, GREEN, (bar_x, hp_bar_y, hp_bar_width, bar_height))
                    # Contour de la barre
                    pygame.draw.rect(self.screen, BLACK, (bar_x, hp_bar_y, bar_width, bar_height), 1)
                    
                    # Barre de stamina (bleue) - positionnée 6 pixels plus bas
                    stamina_bar_y = y * CELL_SIZE + CELL_SIZE - 6  # -12 + 6 = -6
                    stamina_ratio = animal.stamina / animal.max_stamina
                    
                    # Dessiner une petite icône d'éclair pour la stamina
                    bolt_size = 8
                    bolt_x = bar_x - bolt_size - 2
                    bolt_y = stamina_bar_y + bar_height // 2 - bolt_size // 2
                    
                    # Dessiner un éclair jaune
                    pygame.draw.polygon(self.screen, YELLOW, [
                        (bolt_x + bolt_size // 2, bolt_y),
                        (bolt_x + bolt_size, bolt_y + bolt_size // 2),
                        (bolt_x + bolt_size // 2, bolt_y + bolt_size // 2),
                        (bolt_x + bolt_size // 2, bolt_y + bolt_size),
                        (bolt_x, bolt_y + bolt_size // 2),
                        (bolt_x + bolt_size // 2, bolt_y + bolt_size // 2)
                    ])
                    
                    # Fond de la barre (gris)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (bar_x, stamina_bar_y, bar_width, bar_height))
                    # Barre de stamina (bleue)
                    stamina_bar_width = max(int(bar_width * stamina_ratio), 1)  # Au moins 1 pixel de large
                    pygame.draw.rect(self.screen, BLUE, (bar_x, stamina_bar_y, stamina_bar_width, bar_height))
                    # Contour de la barre
                    pygame.draw.rect(self.screen, BLACK, (bar_x, stamina_bar_y, bar_width, bar_height), 1)
                    
                    # Afficher les valeurs numériques à l'intérieur des barres
                    hp_font = pygame.font.SysFont(None, 14)
                    hp_text = hp_font.render(f"{animal.hp}/{animal.max_hp}", True, BLACK)
                    stamina_text = hp_font.render(f"{animal.stamina}/{animal.max_stamina}", True, BLACK)
                    
                    # Centrer les textes dans les barres
                    hp_text_rect = hp_text.get_rect(center=(bar_x + bar_width // 2, hp_bar_y + bar_height // 2))
                    stamina_text_rect = stamina_text.get_rect(center=(bar_x + bar_width // 2, stamina_bar_y + bar_height // 2))
                    
                    self.screen.blit(hp_text, hp_text_rect)
                    self.screen.blit(stamina_text, stamina_text_rect)
                    
                    # Ajouter des barres de faim et de soif
                    hunger_bar_y = stamina_bar_y + bar_height + 2
                    thirst_bar_y = hunger_bar_y + bar_height + 2
                    
                    # Calculer les ratios
                    hunger_ratio = animal.hunger / animal.max_hunger
                    thirst_ratio = animal.thirst / animal.max_thirst
                    
                    # Dessiner une icône de nourriture pour la faim
                    food_size = 8
                    food_x = bar_x - food_size - 2
                    food_y = hunger_bar_y + bar_height // 2 - food_size // 2
                    
                    # Dessiner une pomme rouge
                    pygame.draw.circle(self.screen, (255, 0, 0), (food_x + food_size // 2, food_y + food_size // 2), food_size // 2)
                    pygame.draw.rect(self.screen, (0, 100, 0), (food_x + food_size // 2 - 1, food_y, 2, food_size // 3))
                    
                    # Dessiner une icône d'eau pour la soif
                    water_size = 8
                    water_x = bar_x - water_size - 2
                    water_y = thirst_bar_y + bar_height // 2 - water_size // 2
                    
                    # Dessiner une goutte d'eau bleue
                    pygame.draw.polygon(self.screen, (0, 100, 255), [
                        (water_x + water_size // 2, water_y),
                        (water_x + water_size, water_y + water_size // 2),
                        (water_x + water_size // 2, water_y + water_size),
                        (water_x, water_y + water_size // 2)
                    ])
                    
                    # Fond de la barre de faim (gris)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (bar_x, hunger_bar_y, bar_width, bar_height))
                    # Barre de faim (orange)
                    hunger_bar_width = max(int(bar_width * hunger_ratio), 1)  # Au moins 1 pixel de large
                    pygame.draw.rect(self.screen, ORANGE, (bar_x, hunger_bar_y, hunger_bar_width, bar_height))
                    # Contour de la barre
                    pygame.draw.rect(self.screen, BLACK, (bar_x, hunger_bar_y, bar_width, bar_height), 1)
                    
                    # Fond de la barre de soif (gris)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (bar_x, thirst_bar_y, bar_width, bar_height))
                    # Barre de soif (bleu clair)
                    thirst_bar_width = max(int(bar_width * thirst_ratio), 1)  # Au moins 1 pixel de large
                    pygame.draw.rect(self.screen, LIGHT_BLUE, (bar_x, thirst_bar_y, thirst_bar_width, bar_height))
                    # Contour de la barre
                    pygame.draw.rect(self.screen, BLACK, (bar_x, thirst_bar_y, bar_width, bar_height), 1)
                    
                    # Afficher les valeurs numériques à l'intérieur des barres de faim et de soif
                    hunger_text = hp_font.render(f"{int(animal.hunger / animal.max_hunger * 100)}%", True, BLACK)
                    thirst_text = hp_font.render(f"{int(animal.thirst)}%", True, BLACK)
                    
                    # Centrer les textes dans les barres
                    hunger_text_rect = hunger_text.get_rect(center=(bar_x + bar_width // 2, hunger_bar_y + bar_height // 2))
                    thirst_text_rect = thirst_text.get_rect(center=(bar_x + bar_width // 2, thirst_bar_y + bar_height // 2))
                    
                    self.screen.blit(hunger_text, hunger_text_rect)
                    self.screen.blit(thirst_text, thirst_text_rect)
        
        # Dessiner l'animal en cours d'animation
        if self.animation_in_progress and self.animating_animal:
            # Calculer la position intermédiaire
            progress = self.animation_current_frame / self.animation_frames
            start_x, start_y = self.terrain.position_to_coordinates(self.animation_start_pos)
            end_x, end_y = self.terrain.position_to_coordinates(self.animation_end_pos)
            
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            # Calculer le centre de la cellule pour l'animation
            cell_center_x = current_x * CELL_SIZE + CELL_SIZE // 2
            cell_center_y = current_y * CELL_SIZE + CELL_SIZE // 2
            
            # Dessiner l'image de l'animal en animation
            if self.animating_animal.name in self.images:
                animal_img = self.images[self.animating_animal.name]
            else:
                animal_img = self.images["default"]
            img_rect = animal_img.get_rect(center=(cell_center_x, cell_center_y))
            self.screen.blit(animal_img, img_rect)

    def draw_info_panel(self):
        # Dessiner le fond du panneau d'information
        info_rect = pygame.Rect(self.terrain.width * CELL_SIZE, 0, INFO_WIDTH, self.height)
        pygame.draw.rect(self.screen, WHITE, info_rect)
        pygame.draw.line(self.screen, BLACK, (self.terrain.width * CELL_SIZE, 0), (self.terrain.width * CELL_SIZE, self.height), 2)
        
        # Titre du jeu
        title = self.font.render("Jeu des Animaux", True, BLACK)
        self.screen.blit(title, (self.terrain.width * CELL_SIZE + 10, 10))
        
        # Afficher les informations sur l'animal sélectionné
        if self.selected_animal:
            # Nom de l'animal
            name_text = self.font.render(f"{self.selected_animal.name}", True, BLACK)
            self.screen.blit(name_text, (self.terrain.width * CELL_SIZE + 10, 50))
            
            # Ligne de séparation pour les statistiques
            pygame.draw.line(self.screen, GRAY, 
                            (self.terrain.width * CELL_SIZE + 5, 75), 
                            (self.terrain.width * CELL_SIZE + INFO_WIDTH - 5, 75), 1)
            
            # Titre des statistiques
            stats_title = self.small_font.render("Statistiques:", True, BLACK)
            self.screen.blit(stats_title, (self.terrain.width * CELL_SIZE + 10, 80))
            
            # Statistiques de base
            y_offset = 100
            line_height = 20
            
            # Points de vie
            hp_text = self.small_font.render(f"HP: {self.selected_animal.hp}/{self.selected_animal.max_hp}", True, RED)
            self.screen.blit(hp_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Stamina
            stamina_text = self.small_font.render(f"Stamina: {self.selected_animal.stamina}/{self.selected_animal.max_stamina}", True, BLUE)
            self.screen.blit(stamina_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Vitesse
            speed_text = self.small_font.render(f"Vitesse: {self.selected_animal.speed}", True, GREEN)
            self.screen.blit(speed_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Points de vitesse
            speed_points_text = self.small_font.render(f"Points de vitesse: {self.selected_animal.speed_points}", True, GREEN)
            self.screen.blit(speed_points_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Nouvelles caractéristiques
            # Dents
            teeth_text = self.small_font.render(f"Dents: {self.selected_animal.teeth}", True, YELLOW)
            self.screen.blit(teeth_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Griffes
            claws_text = self.small_font.render(f"Griffes: {self.selected_animal.claws}", True, ORANGE)
            self.screen.blit(claws_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Peau
            skin_text = self.small_font.render(f"Peau: {self.selected_animal.skin}", True, BROWN)
            self.screen.blit(skin_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Taille
            height_text = self.small_font.render(f"Taille: {self.selected_animal.height}", True, PURPLE)
            self.screen.blit(height_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Faim
            hunger_text = self.small_font.render(f"Faim: {int(self.selected_animal.hunger)}/{self.selected_animal.max_hunger}", True, ORANGE)
            self.screen.blit(hunger_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Soif
            thirst_text = self.small_font.render(f"Soif: {int(self.selected_animal.thirst)}/{self.selected_animal.max_thirst}", True, LIGHT_BLUE)
            self.screen.blit(thirst_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            y_offset += line_height
            
            # Ligne de séparation pour le statut
            pygame.draw.line(self.screen, GRAY, 
                            (self.terrain.width * CELL_SIZE + 5, y_offset + 5), 
                            (self.terrain.width * CELL_SIZE + INFO_WIDTH - 5, y_offset + 5), 1)
            y_offset += 10
            
            # Indiquer si c'est le tour de cet animal
            if self.selected_animal == self.current_animal:
                turn_text = self.small_font.render("C'est son tour de jouer!", True, GREEN)
                self.screen.blit(turn_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height + 10
                
                # Ligne de séparation pour les commandes
                pygame.draw.line(self.screen, GRAY, 
                                (self.terrain.width * CELL_SIZE + 5, y_offset), 
                                (self.terrain.width * CELL_SIZE + INFO_WIDTH - 5, y_offset), 1)
                y_offset += 10
                
                # Afficher les commandes
                commands_title = self.small_font.render("Commandes:", True, BLACK)
                self.screen.blit(commands_title, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height + 5
                
                # Déplacements
                move_text = self.small_font.render("- Clic: Marcher", True, BLUE)
                self.screen.blit(move_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height
                
                run_text = self.small_font.render(f"- Shift+Clic: Courir (+{RUN_SPEED_GAIN} vitesse)", True, (50, 50, 200))
                self.screen.blit(run_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height + 5
                
                # Attaques
                attack_title = self.small_font.render("Sur un ennemi:", True, BLACK)
                self.screen.blit(attack_title, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height
                
                # Calculer les dégâts réels en fonction des caractéristiques
                slap_damage = SLAP_DAMAGE + self.selected_animal.claws
                bite_damage = BITE_DAMAGE + self.selected_animal.teeth
                
                slap_text = self.small_font.render(f"- Clic: Gifler ({slap_damage} dégâts, +{SLAP_SPEED_GAIN} vitesse)", True, RED)
                self.screen.blit(slap_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
                y_offset += line_height
                
                bite_text = self.small_font.render(f"- Shift+Clic: Mordre ({bite_damage} dégâts)", True, (200, 0, 0))
                self.screen.blit(bite_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
            else:
                turn_text = self.small_font.render("En attente de son tour...", True, RED)
                self.screen.blit(turn_text, (self.terrain.width * CELL_SIZE + 10, y_offset))
        
        # Afficher le message d'information
        if self.info_message and self.info_message_timer > 0:
            info_text = self.small_font.render(self.info_message, True, BLACK)
            info_rect = info_text.get_rect(center=(self.terrain.width * CELL_SIZE + INFO_WIDTH // 2, self.height - 50))
            self.screen.blit(info_text, info_rect)
        
        # Afficher le statut du jeu
        if self.game.game_over:
            game_over_text = self.font.render("Jeu terminé!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(self.terrain.width * CELL_SIZE + INFO_WIDTH // 2, self.height - 100))
            self.screen.blit(game_over_text, game_over_rect)
            
            if self.game.winner:
                winner_text = self.font.render(f"{self.game.winner.name} a gagné!", True, GREEN)
                winner_rect = winner_text.get_rect(center=(self.terrain.width * CELL_SIZE + INFO_WIDTH // 2, self.height - 70))
                self.screen.blit(winner_text, winner_rect)

    def handle_click(self, pos, shift_pressed=False):
        """Gère les clics sur le terrain
        
        Args:
            pos: Position du clic (x, y)
            shift_pressed: True si la touche Shift est enfoncée, False sinon
        """
        # Si une animation est en cours ou si le jeu est terminé, ne rien faire
        if self.animation_in_progress or self.game.game_over:
            return
        
        # Vérifier si le clic est sur le terrain
        x, y = pos
        
        if x < self.terrain.width * CELL_SIZE and y < self.terrain.height * CELL_SIZE:
            grid_x = x // CELL_SIZE
            grid_y = y // CELL_SIZE
            position = self.terrain.coordinates_to_position(grid_x, grid_y)
            
            # Si un animal est sélectionné et que c'est son tour
            if self.selected_animal and self.selected_animal == self.current_animal:
                # Récupérer les actions possibles
                actions = self.game.get_animal_possible_actions(self.selected_animal)
                
                # Vérifier si le clic est sur un animal (pour attaquer)
                animal = self.terrain.get_animal_at(position)
                if animal and animal != self.selected_animal:
                    # Déterminer l'action en fonction de la touche Shift
                    action_name = "bite" if shift_pressed else "slap"
                    
                    # Vérifier si l'action est possible
                    if action_name in actions and animal in actions[action_name]:
                        # Exécuter l'action
                        result = self.game.play_turn(self.selected_animal, action_name, animal)
                        if result:
                            # Afficher le message approprié
                            if action_name == "bite":
                                self.show_info_message(f"{self.selected_animal.name} a mordu {animal.name} et infligé {BITE_DAMAGE} dégâts")
                            else:  # slap
                                self.show_info_message(f"{self.selected_animal.name} a giflé {animal.name}, infligé {SLAP_DAMAGE} dégâts et récupéré {SLAP_SPEED_GAIN} points de vitesse")
                            
                            # Mettre à jour l'animal actuel après l'action
                            self.current_animal = self.game.get_next_animal_to_play()
                            
                            # Vérifier si des fruits sont apparus
                            self.check_for_new_fruits()
                            
                            # Si le nouvel animal actuel est différent, le sélectionner automatiquement
                            if self.current_animal and self.current_animal != self.selected_animal:
                                self.selected_animal = self.current_animal
                                self.update_highlights()
                            elif not self.current_animal:
                                # Si aucun animal n'est prêt à jouer, désélectionner l'animal actuel
                                self.selected_animal = None
                                self.update_highlights()
                        else:
                            self.show_info_message(f"Action {action_name} impossible")
                
                # Vérifier si le clic est sur une case vide (pour se déplacer)
                elif not animal:
                    # Vérifier si c'est une case d'eau (pour boire)
                    square = self.terrain.get_square(position)
                    if square and square.terrain_type == Square.TYPE_WATER and "drink" in actions and position in actions["drink"]:
                        # Exécuter l'action de boire
                        result = self.game.play_turn(self.selected_animal, "drink", position)
                        
                        if result:
                            # Afficher le message approprié
                            self.show_info_message(f"{self.selected_animal.name} a bu de l'eau et récupéré {WATER_THIRST_RECOVERY} points de soif")
                            
                            # Mettre à jour l'animal actuel après l'action
                            self.current_animal = self.game.get_next_animal_to_play()
                            
                            # Vérifier si des fruits sont apparus
                            self.check_for_new_fruits()
                            
                            # Si le nouvel animal actuel est différent, le sélectionner automatiquement
                            if self.current_animal and self.current_animal != self.selected_animal:
                                self.selected_animal = self.current_animal
                                self.update_highlights()
                            elif not self.current_animal:
                                # Si aucun animal n'est prêt à jouer, désélectionner l'animal actuel
                                self.selected_animal = None
                                self.update_highlights()
                        else:
                            self.show_info_message("Impossible de boire ici")
                    else:
                        # Déterminer l'action en fonction de la touche Shift
                        action_name = "run" if shift_pressed else "walk"
                        
                        # Vérifier si l'action est possible
                        if action_name in actions and position in actions[action_name]:
                            # Exécuter l'action
                            old_position = self.selected_animal.position
                            result = self.game.play_turn(self.selected_animal, action_name, position)
                            
                            if result:
                                # Décomposer le résultat
                                success, fruit_consumed = result if isinstance(result, tuple) else (result, False)
                                
                                # Démarrer l'animation
                                self.start_animation(self.selected_animal, old_position, position)
                                
                                # Afficher le message approprié
                                if fruit_consumed:
                                    resource_type = self.terrain.get_resource_at(position)
                                    if resource_type and resource_type.name == "GreenFruit":
                                        self.show_info_message(f"{self.selected_animal.name} a mangé un fruit vert et récupéré {GREEN_FRUIT_HEAL_AMOUNT} PV et {GREEN_FRUIT_HUNGER_RECOVERY} points de faim")
                                    elif resource_type and resource_type.name == "RedFruit":
                                        self.show_info_message(f"{self.selected_animal.name} a mangé un fruit rouge et récupéré {RED_FRUIT_STAMINA_RECOVERY} stamina et {RED_FRUIT_HUNGER_RECOVERY} points de faim")
                                    else:
                                        self.show_info_message(f"{self.selected_animal.name} a mangé un fruit et récupéré {FRUIT_HEAL_AMOUNT} PV, {FRUIT_STAMINA_RECOVERY} stamina et {FRUIT_HUNGER_RECOVERY} points de faim")
                                else:
                                    if action_name == "run":
                                        self.show_info_message(f"{self.selected_animal.name} a couru et récupéré {RUN_SPEED_GAIN} points de vitesse")
                                    else:
                                        self.show_info_message(f"{self.selected_animal.name} a marché jusqu'à la position {position}")
                                
                                # Mettre à jour l'animal actuel après l'action
                                self.current_animal = self.game.get_next_animal_to_play()
                                
                                # Vérifier si des fruits sont apparus
                                self.check_for_new_fruits()
                                
                                # Si le nouvel animal actuel est différent, le sélectionner automatiquement
                                if self.current_animal and self.current_animal != self.selected_animal:
                                    self.selected_animal = self.current_animal
                                    self.update_highlights()
                                elif not self.current_animal:
                                    # Si aucun animal n'est prêt à jouer, désélectionner l'animal actuel
                                    self.selected_animal = None
                                    self.update_highlights()
                            else:
                                self.show_info_message(f"Action {action_name} impossible")
                        else:
                            self.show_info_message(f"Action {action_name} impossible")
            
            # Si aucun animal n'est sélectionné ou si ce n'est pas son tour
            else:
                # Vérifier si le clic est sur un animal
                animal = self.terrain.get_animal_at(position)
                if animal:
                    # Sélectionner l'animal
                    self.selected_animal = animal
                    self.update_highlights()
                    
                    # Si c'est le tour de cet animal, afficher un message
                    if animal == self.current_animal:
                        self.show_info_message(f"C'est au tour de {animal.name}")
                    else:
                        self.show_info_message(f"Ce n'est pas le tour de {animal.name}")

    def start_animation(self, animal, start_pos, end_pos):
        self.animation_in_progress = True
        self.animation_current_frame = 0
        self.animation_start_pos = start_pos
        self.animation_end_pos = end_pos
        self.animating_animal = animal

    def update_animation(self):
        if not self.animation_in_progress:
            return
            
        self.animation_current_frame += 1
        
        if self.animation_current_frame >= self.animation_frames:
            self.animation_in_progress = False
            self.animating_animal = None

    def update_highlights(self):
        """Met à jour les cellules et animaux mis en évidence"""
        self.highlighted_cells = []
        self.highlighted_animals = []
        
        if self.selected_animal and self.selected_animal == self.current_animal:
            actions = self.game.get_animal_possible_actions(self.selected_animal)
            
            # Mettre en évidence les cellules pour les déplacements
            if "walk" in actions:
                self.highlighted_cells.extend(actions["walk"])
            
            # Mettre en évidence les cases d'eau pour boire
            if "drink" in actions:
                self.highlighted_cells.extend(actions["drink"])
            
            # Mettre en évidence les animaux pour les attaques
            if "bite" in actions:
                self.highlighted_animals.extend(actions["bite"])
            if "slap" in actions:
                self.highlighted_animals.extend(actions["slap"])

    def reset_selection(self):
        """Réinitialise la sélection"""
        self.selected_action = None
        self.highlighted_cells = []
        self.highlighted_animals = []

    def update_buttons(self, pos):
        """Met à jour les boutons en fonction de la position de la souris"""
        pass  # Plus de boutons à mettre à jour

    def show_info_message(self, message, duration=120):  # 120 frames = 2 secondes à 60 FPS
        """Affiche un message d'information temporaire"""
        self.info_message = message
        self.info_message_timer = duration

    def check_for_new_fruits(self):
        """Vérifie si de nouveaux fruits sont apparus et affiche un message"""
        # Récupérer les positions des fruits initiaux
        initial_fruit_positions = set(GREEN_FRUIT_POSITIONS) | set(RED_FRUIT_POSITIONS)
        
        # Récupérer les positions actuelles des fruits
        current_fruit_positions = set(self.game.terrain.resources.keys())
        
        # Trouver les nouvelles positions de fruits
        new_fruit_positions = current_fruit_positions - initial_fruit_positions
        
        # Afficher un message si des fruits sont apparus
        if new_fruit_positions:
            if len(new_fruit_positions) == 1:
                self.show_info_message(f"Un fruit est apparu à la position {list(new_fruit_positions)[0]}!")
            else:
                self.show_info_message(f"{len(new_fruit_positions)} fruits sont apparus!")

    def draw_speed_bar(self):
        """Dessine la barre de vitesse montrant la position des animaux en fonction de leurs points de vitesse"""
        # Dimensions et position de la barre
        bar_width = 600
        bar_height = 40
        bar_x = (self.width - bar_width) // 2
        bar_y = self.terrain.height * CELL_SIZE + 20  # Positionner sous la grille du terrain
        
        # Dessiner un fond pour la section de la barre de vitesse
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, self.terrain.height * CELL_SIZE, self.width, 80))
        
        # Titre de la barre
        title_text = self.font.render("Points de vitesse", True, BLACK)
        title_rect = title_text.get_rect(center=(self.width // 2, bar_y - 10))
        self.screen.blit(title_text, title_rect)
        
        # Dessiner le fond de la barre
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
        
        # Dessiner les graduations
        for i in range(11):  # 0, 10, 20, ..., 100
            pos_x = bar_x + (i * bar_width // 10)
            pygame.draw.line(self.screen, GRAY, (pos_x, bar_y), (pos_x, bar_y + bar_height), 1)
            
            # Ajouter les valeurs numériques
            if i % 2 == 0:  # 0, 20, 40, 60, 80, 100
                value_text = self.small_font.render(str(i * 10), True, BLACK)
                self.screen.blit(value_text, (pos_x - 10, bar_y + bar_height + 5))
        
        # Dessiner le contour de la barre
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Dessiner la position de chaque animal sur la barre
        for animal in self.game.animals:
            if animal.is_alive:
                # Calculer la position en fonction des points de vitesse (limité à l'affichage de 0-100)
                speed_points_display = min(100, animal.speed_points)  # Pour l'affichage sur la barre
                position_x = bar_x + int(speed_points_display * bar_width / 100)
                position_x = min(bar_x + bar_width - 10, max(bar_x + 10, position_x))  # Limiter à la largeur de la barre
                
                # Déterminer la couleur (Lion = jaune, Tigre = orange)
                color = YELLOW if animal.name == "Lion" else ORANGE
                
                # Dessiner un cercle pour représenter l'animal
                pygame.draw.circle(self.screen, color, (position_x, bar_y + bar_height // 2), 12)
                
                # Ajouter un contour plus épais pour l'animal actuel
                if animal == self.current_animal:
                    pygame.draw.circle(self.screen, BLACK, (position_x, bar_y + bar_height // 2), 12, 2)
                
                # Ajouter le nom de l'animal et ses points de vitesse
                name_text = self.small_font.render(f"{animal.name}: {animal.speed_points}", True, BLACK)
                name_rect = name_text.get_rect(center=(position_x, bar_y + bar_height // 2))
                # Dessiner un fond blanc pour le texte pour une meilleure lisibilité
                text_bg_rect = name_rect.copy()
                text_bg_rect.inflate_ip(10, 6)
                text_bg_rect.y -= 20
                pygame.draw.rect(self.screen, WHITE, text_bg_rect)
                pygame.draw.rect(self.screen, BLACK, text_bg_rect, 1)
                name_rect.y -= 20
                self.screen.blit(name_text, name_rect) 