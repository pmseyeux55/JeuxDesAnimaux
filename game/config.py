"""
Configuration du jeu des animaux.
Ce fichier centralise tous les paramètres du jeu pour faciliter les modifications.
"""

# Paramètres de conversion des points de caractéristiques
HP_CONVERSION = 2  # Nombre de points de caractéristique nécessaires pour 1 point de vie
STAMINA_CONVERSION = 1  # Nombre de points de caractéristique nécessaires pour 1 point de stamina
SPEED_CONVERSION = 5  # Nombre de points de caractéristique nécessaires pour 1 point de vitesse
TEETH_CONVERSION = 3  # Nombre de points de caractéristique nécessaires pour 1 point de teeth
CLAWS_CONVERSION = 3  # Nombre de points de caractéristique nécessaires pour 1 point de claws
SKIN_CONVERSION = 3  # Nombre de points de caractéristique nécessaires pour 1 point de skin
HEIGHT_CONVERSION = 1  # Nombre de points de caractéristique nécessaires pour 1 point de height

# Paramètres des actions
# Déplacements
WALK_COST = 0  # Coût en stamina pour marcher
RUN_COST = 1  # Coût en stamina pour courir
RUN_SPEED_GAIN = 50  # Gain de points de vitesse pour courir
WALK_HUNGER_LOSS = 1  # Perte de faim par point de vitesse en marchant
RUN_HUNGER_LOSS = 2  # Perte de faim par point de vitesse en courant
WALK_THIRST_LOSS = 10  # Perte de soif en marchant
RUN_THIRST_LOSS = 15  # Perte de soif en courant

# Attaques
BITE_COST = 2  # Coût en stamina pour mordre
BITE_DAMAGE = 3  # Dégâts de base infligés par une morsure
TEETH_DAMAGE_BONUS = 1  # Bonus de dégâts par point de teeth
SLAP_COST = 1  # Coût en stamina pour gifler
SLAP_DAMAGE = 1  # Dégâts de base infligés par une gifle
CLAWS_DAMAGE_BONUS = 1  # Bonus de dégâts par point de claws
SLAP_SPEED_GAIN = 50  # Gain de points de vitesse pour gifler
# SKIN_DEFENSE_FACTOR = 0.1  # Réduction des dégâts de gifle par point de skin (en pourcentage)
# Maintenant, skin réduit directement les dégâts de slap (1 point de skin = 1 point de dégât réduit)
HEIGHT_DODGE_FACTOR = 0.1  # Chance d'esquiver une morsure par point de différence de height (en pourcentage)

# Paramètres de configuration des animaux
MAX_POINTS = 100  # Points totaux à répartir

# Valeurs minimales et maximales pour chaque statistique
HP_MIN = 5
HP_MAX = 50
STAMINA_MIN = 5
STAMINA_MAX = 50
SPEED_MIN = 2
SPEED_MAX = 10
TEETH_MIN = 2
TEETH_MAX = 30
CLAWS_MIN = 1
CLAWS_MAX = 10
SKIN_MIN = 0
SKIN_MAX = 50  # Valeur par défaut pour skin
HEIGHT_MIN = 20
HEIGHT_MAX = 100

# Paramètres du terrain
TERRAIN_WIDTH = 10  # Largeur du terrain
TERRAIN_HEIGHT = 10  # Hauteur du terrain

# Positions initiales des animaux
LION_START_POSITION = 1  # Position de départ du lion
TIGER_START_POSITION = 100  # Position de départ du tigre

# Positions des fruits
# FRUIT_POSITIONS = [34, 37, 64, 67]  # Positions des fruits sur le terrain 
GREEN_FRUIT_POSITIONS = [34, 64]  # Positions des fruits verts sur le terrain
RED_FRUIT_POSITIONS = [37, 67]  # Positions des fruits rouges sur le terrain

# Paramètres des cases (Square)
SQUARE_SPEED = 1  # Vitesse de base des cases
SQUARE_FRUIT_PROBABILITY = 0.01  # Probabilité qu'une case génère un fruit quand elle atteint 100 points de vitesse
SQUARE_INITIAL_SPEED_POINTS = 100  # Points de vitesse initiaux des cases

# Ressources
FRUIT_VALUE = 5  # Valeur de base d'un fruit
FRUIT_HEAL_AMOUNT = 5  # Quantité de points de vie récupérés en mangeant un fruit
FRUIT_STAMINA_RECOVERY = 2  # Quantité de stamina récupérée en mangeant un fruit
FRUIT_HUNGER_RECOVERY = 200  # Quantité de points de faim récupérés en mangeant un fruit

# Paramètres des fruits spécifiques
GREEN_FRUIT_HEAL_AMOUNT = 2  # Quantité de points de vie récupérés en mangeant un fruit vert
GREEN_FRUIT_STAMINA_RECOVERY = 0  # Pas de récupération de stamina pour le fruit vert
GREEN_FRUIT_HUNGER_RECOVERY = 150  # Quantité de points de faim récupérés en mangeant un fruit vert

RED_FRUIT_HEAL_AMOUNT = 0  # Pas de récupération de points de vie pour le fruit rouge
RED_FRUIT_STAMINA_RECOVERY = 5  # Quantité de stamina récupérée en mangeant un fruit rouge
RED_FRUIT_HUNGER_RECOVERY = 200  # Quantité de points de faim récupérés en mangeant un fruit rouge

# Couleurs (format RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150, 150, 150)  # Pour les boutons inactifs
BLUE = (100, 100, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
DARK_BLUE = (50, 50, 200)
LIGHT_BLUE = (180, 180, 255)
DARK_RED = (200, 0, 0)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
LIGHT_RED = (255, 230, 230)  # Couleur de fond pour les cases fruitières
READY_RED = (255, 180, 180)  # Couleur plus vive pour les cases fruitières prêtes à produire un fruit 
PURPLE = (180, 0, 255)  # Couleur pour la taille 

# Paramètres de récupération de soif
WATER_THIRST_RECOVERY = 80  # Quantité de points de soif récupérés en buvant de l'eau

# Paramètres de dégâts par faim et soif
HUNGER_DAMAGE = 1  # Dégâts infligés par tour quand la faim est à 0
THIRST_DAMAGE = 1  # Dégâts infligés par tour quand la soif est à 0 