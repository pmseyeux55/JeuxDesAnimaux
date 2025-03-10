"""
Module définissant la classe Square (case du terrain)
"""
from game.config import (
    TERRAIN_WIDTH, TERRAIN_HEIGHT,
    SQUARE_SPEED, SQUARE_FRUIT_PROBABILITY, SQUARE_INITIAL_SPEED_POINTS,
    WATER_THIRST_RECOVERY
)
import random

class Square:
    """Représente une case du terrain de jeu"""
    
    # Types de terrain possibles
    TYPE_NORMAL = "normal"  # Terrain normal
    TYPE_WATER = "water"    # Eau (pourrait ralentir les animaux)
    TYPE_FOREST = "forest"  # Forêt (pourrait cacher les animaux)
    TYPE_MOUNTAIN = "mountain"  # Montagne (pourrait être infranchissable)
    
    def __init__(self, x, y, terrain_type=TYPE_NORMAL, is_orchard=False):
        """Initialise une case du terrain
        
        Args:
            x: Coordonnée x de la case
            y: Coordonnée y de la case
            terrain_type: Type de terrain (normal, eau, forêt, montagne)
            is_orchard: Si True, la case peut produire des fruits
        """
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.animal = None  # Animal présent sur la case
        self.resource = None  # Ressource présente sur la case
        self.speed = SQUARE_SPEED  # Vitesse de base de la case
        self.speed_points = SQUARE_INITIAL_SPEED_POINTS  # Points de vitesse initiaux
        self.is_orchard = is_orchard  # Si True, la case peut produire des fruits
        
    @property
    def position(self):
        """Retourne la position de la case (1-100)"""
        return self.y * TERRAIN_WIDTH + self.x + 1
        
    @property
    def is_occupied(self):
        """Vérifie si la case est occupée par un animal"""
        return self.animal is not None
        
    @property
    def has_resource(self):
        """Vérifie si la case contient une ressource"""
        return self.resource is not None
        
    def place_animal(self, animal):
        """Place un animal sur la case
        
        Args:
            animal: Animal à placer sur la case
            
        Returns:
            bool: True si l'animal a été placé, False sinon
        """
        if not self.is_occupied:
            self.animal = animal
            animal.position = self.position
            return True
        return False
        
    def remove_animal(self):
        """Retire l'animal de la case
        
        Returns:
            Animal: L'animal qui était sur la case, ou None
        """
        animal = self.animal
        self.animal = None
        return animal
        
    def place_resource(self, resource):
        """Place une ressource sur la case
        
        Args:
            resource: Ressource à placer sur la case
            
        Returns:
            bool: True si la ressource a été placée, False sinon
        """
        if not self.has_resource:
            self.resource = resource
            resource.position = self.position
            return True
        return False
        
    def remove_resource(self):
        """Retire la ressource de la case
        
        Returns:
            Resource: La ressource qui était sur la case, ou None
        """
        resource = self.resource
        self.resource = None
        # Réinitialiser les points de vitesse lorsque le fruit est mangé
        self.speed_points = 0
        return resource
        
    def on_enter(self, animal):
        """Méthode appelée lorsqu'un animal entre sur la case
        
        Args:
            animal: Animal qui entre sur la case
            
        Returns:
            dict: Effets appliqués à l'animal
        """
        effects = {}
        
        # Appliquer les effets du type de terrain
        if self.terrain_type == self.TYPE_WATER:
            # L'eau permet à l'animal de boire et de récupérer des points de soif
            thirst_recovered = animal.recover_thirst(WATER_THIRST_RECOVERY)
            effects["thirst"] = thirst_recovered
            # L'eau ralentit toujours l'animal
            effects["speed"] = -10
        elif self.terrain_type == self.TYPE_FOREST:
            # La forêt pourrait donner un bonus de stamina
            effects["stamina"] = 1
            
        # Vérifier s'il y a une ressource à consommer
        if self.has_resource:
            resource = self.resource
            # Si c'est un fruit, le consommer
            if hasattr(resource, "consume"):
                hp_recovered, stamina_recovered, hunger_recovered = resource.consume(animal)
                if hp_recovered > 0:
                    effects["heal"] = hp_recovered
                if stamina_recovered > 0:
                    effects["stamina"] = stamina_recovered
                if hunger_recovered > 0:
                    effects["hunger"] = hunger_recovered
                self.remove_resource()
                
        return effects
        
    def can_move_to(self, animal):
        """Vérifie si un animal peut se déplacer sur cette case
        
        Args:
            animal: Animal qui veut se déplacer sur la case
            
        Returns:
            bool: True si l'animal peut se déplacer sur la case, False sinon
        """
        # Une case avec un animal ne peut pas être occupée
        if self.is_occupied:
            return False
            
        # Une montagne est infranchissable
        if self.terrain_type == self.TYPE_MOUNTAIN:
            return False
            
        # Une tuile d'eau est infranchissable
        if self.terrain_type == self.TYPE_WATER:
            return False
            
        return True
    
    def add_speed_points(self):
        """Ajoute des points de vitesse à la case en fonction de sa vitesse de base
        
        Returns:
            bool: True si la case a atteint 100 points de vitesse, False sinon
        """
        # Si la case a déjà 100 points ou plus, ne rien faire
        if self.speed_points >= 100:
            return True
            
        # Ajouter des points de vitesse
        self.speed_points += self.speed
        
        # Vérifier si la case a atteint 100 points
        return self.speed_points >= 100
    
    def try_generate_fruit(self, fruit_class):
        """Essaie de générer un fruit sur la case
        
        Args:
            fruit_class: Classe de fruit à générer
            
        Returns:
            bool: True si un fruit a été généré, False sinon
        """
        import random
        from game.resources import GreenFruit, RedFruit
        
        # Vérifier si la case est un verger
        if not self.is_orchard:
            return False
            
        # Vérifier si la case est vide
        if self.is_occupied or self.has_resource:
            return False
            
        # Générer un fruit avec une certaine probabilité
        if random.random() < 0.05:  # 5% de chance
            # Choisir aléatoirement entre un fruit vert et un fruit rouge
            if random.choice([True, False]):
                fruit = GreenFruit(position=self.position)
            else:
                fruit = RedFruit(position=self.position)
                
            # Placer le fruit sur la case
            if self.place_resource(fruit):
                print(f"Fruit généré à la position {self.position}!")
                return True
            
        return False
        
    def __str__(self):
        """Représentation textuelle de la case"""
        content = "A" if self.is_occupied else "R" if self.has_resource else " "
        return f"[{content}]" 