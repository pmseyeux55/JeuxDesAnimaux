from game.config import (
    WALK_COST, RUN_COST, RUN_SPEED_GAIN,
    WALK_HUNGER_LOSS, RUN_HUNGER_LOSS, WALK_THIRST_LOSS, RUN_THIRST_LOSS,
    BITE_COST, BITE_DAMAGE, TEETH_DAMAGE_BONUS,
    SLAP_COST, SLAP_DAMAGE, CLAWS_DAMAGE_BONUS, SLAP_SPEED_GAIN,
    HEIGHT_DODGE_FACTOR, WATER_THIRST_RECOVERY,
    HUNGER_DAMAGE, THIRST_DAMAGE
)
from game.square import Square
import random

class Animal:
    def __init__(self, name, hp, stamina, speed, position, teeth=1, claws=1, skin=1, height=1):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.speed = speed
        self.speed_points = speed  # Points de vitesse accumulés
        self.position = position
        self.is_alive = True
        
        # Nouvelles caractéristiques
        self.teeth = teeth  # Augmente les dégâts de morsure
        self.claws = claws  # Augmente les dégâts de gifle
        self.skin = skin    # Réduit les dégâts de gifle reçus
        self.height = height  # Chance d'esquiver les morsures
        
        # Attributs de faim et de soif
        self.max_hunger = 100 * self.max_hp
        self.hunger = 100 * self.max_hp  # 100*max_hp = pas faim, 0 = affamé
        self.max_thirst = 100
        self.thirst = 100  # 100 = pas soif, 0 = assoiffé

    def take_damage(self, damage, attack_type="normal"):
        """Inflige des dégâts à l'animal en tenant compte de ses défenses
        
        Args:
            damage: Quantité de dégâts à infliger
            attack_type: Type d'attaque ("bite" ou "slap")
            
        Returns:
            int: Dégâts effectivement infligés
        """
        # Appliquer les réductions de dégâts selon le type d'attaque
        if attack_type == "slap":
            # Réduire les dégâts en fonction de la peau (skin) - réduction directe
            damage = max(0, damage - self.skin)  # Au moins 0 point de dégât
            
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return damage

    def heal(self, amount):
        """Soigne l'animal"""
        self.hp = min(self.hp + amount, self.max_hp)
        return amount

    def use_stamina(self, amount):
        """Utilise de la stamina"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def recover_stamina(self, amount):
        """Récupère de la stamina"""
        self.stamina = min(self.stamina + amount, self.max_stamina)
        return amount

    def add_speed_points(self, points):
        """Ajoute des points de vitesse"""
        self.speed_points += points
        # Pas de limite sur les points de vitesse, tous les points sont conservés
        return points

    def use_speed_points(self, points):
        """Utilise des points de vitesse"""
        if self.speed_points >= points:
            self.speed_points -= points
            return True
        return False

    def walk(self, new_position, terrain):
        """Déplace l'animal d'une case"""
        if terrain.is_valid_move(self.position, new_position, 1) and self.use_stamina(WALK_COST):
            # Consommer de la faim et de la soif
            hunger_loss = (self.max_hp + (self.max_hp - self.hp)) * self.speed
            self.consume_hunger(hunger_loss)
            self.consume_thirst(WALK_THIRST_LOSS)
            return True
        return False

    def run(self, new_position, terrain):
        """Déplace l'animal d'une case en utilisant de la stamina et récupère des points de vitesse"""
        if terrain.is_valid_move(self.position, new_position, 1) and self.use_stamina(RUN_COST):
            # Ajouter des points de vitesse
            self.add_speed_points(RUN_SPEED_GAIN)
            
            # Consommer de la faim et de la soif (plus que pour marcher)
            hunger_loss = (self.max_hp + (self.max_hp - self.hp)) * self.speed * 1.5
            self.consume_hunger(hunger_loss)
            self.consume_thirst(RUN_THIRST_LOSS)  # Courir donne plus soif
            
            return True
        return False

    def bite(self, target, terrain):
        """Attaque un autre animal avec une morsure
        
        La morsure peut manquer sa cible en fonction de la différence de taille (height)
        Les dégâts sont augmentés par les dents (teeth)
        """
        # Vérifier si la cible est adjacente et si l'animal a assez de stamina
        if terrain.is_adjacent(self.position, target.position) and self.use_stamina(BITE_COST):
            # Calculer la différence de taille
            height_diff = max(0, target.height - self.height)
            dodge_chance = height_diff * HEIGHT_DODGE_FACTOR
            
            # Vérifier si la cible esquive l'attaque
            if random.random() < dodge_chance:
                return 0  # L'attaque a manqué
            
            # Calculer les dégâts en tenant compte des dents
            damage = BITE_DAMAGE + (self.teeth * TEETH_DAMAGE_BONUS)
            
            # Infliger les dégâts
            return target.take_damage(damage, attack_type="bite")
        return 0

    def slap(self, target, terrain):
        """Attaque un autre animal avec une gifle et récupère des points de vitesse
        
        Les dégâts sont augmentés par les griffes (claws)
        La cible peut réduire les dégâts grâce à sa peau (skin)
        """
        # Vérifier si la cible est adjacente et si l'animal a assez de stamina
        if terrain.is_adjacent(self.position, target.position) and self.use_stamina(SLAP_COST):
            # Récupérer des points de vitesse
            self.add_speed_points(SLAP_SPEED_GAIN)
            
            # Calculer les dégâts en tenant compte des griffes
            damage = SLAP_DAMAGE + (self.claws * CLAWS_DAMAGE_BONUS)
            
            # Infliger les dégâts (la réduction due à la peau est gérée dans take_damage)
            return target.take_damage(damage, attack_type="slap")
        return 0

    def get_possible_walk_positions(self, terrain):
        """Retourne les positions possibles pour un déplacement de type walk"""
        return terrain.get_valid_moves(self.position, 1)

    def get_possible_run_positions(self, terrain):
        """Retourne les positions possibles pour un déplacement de type run"""
        if self.stamina >= RUN_COST:  # Vérifie si l'animal a assez de stamina pour courir
            # Utiliser distance=1 car run ne déplace plus que d'une case
            return terrain.get_valid_moves(self.position, 1)
        return []

    def consume_hunger(self, amount):
        """Réduit les points de faim de l'animal
        
        Args:
            amount: Quantité de points de faim à réduire
            
        Returns:
            bool: True si l'animal a encore des points de faim, False sinon
        """
        self.hunger = max(0, self.hunger - amount)
        # Si la faim atteint 0, l'animal commence à perdre des points de vie
        if self.hunger == 0:
            self.take_damage(HUNGER_DAMAGE, "hunger")
        return self.hunger > 0
        
    def consume_thirst(self, amount):
        """Réduit les points de soif de l'animal
        
        Args:
            amount: Quantité de points de soif à réduire
            
        Returns:
            bool: True si l'animal a encore des points de soif, False sinon
        """
        self.thirst = max(0, self.thirst - amount)
        # Si la soif atteint 0, l'animal commence à perdre des points de vie
        if self.thirst == 0:
            self.take_damage(THIRST_DAMAGE, "thirst")
        return self.thirst > 0
        
    def recover_hunger(self, amount):
        """Récupère des points de faim
        
        Args:
            amount: Quantité de points de faim à récupérer
            
        Returns:
            int: Quantité de points de faim récupérés
        """
        old_hunger = self.hunger
        self.hunger = min(self.max_hunger, self.hunger + amount)
        return self.hunger - old_hunger
        
    def recover_thirst(self, amount):
        """Récupère des points de soif
        
        Args:
            amount: Quantité de points de soif à récupérer
            
        Returns:
            int: Quantité de points de soif récupérés
        """
        old_thirst = self.thirst
        self.thirst = min(self.max_thirst, self.thirst + amount)
        return self.thirst - old_thirst
        
    def drink(self, water_position, terrain):
        """Boit de l'eau à partir d'une case d'eau adjacente
        
        Args:
            water_position: Position de la case d'eau
            terrain: Terrain du jeu
            
        Returns:
            int: Quantité de points de soif récupérés, 0 si l'action a échoué
        """
        # Vérifier que la case est adjacente
        if not terrain.is_adjacent(self.position, water_position):
            return 0
            
        # Vérifier que la case contient de l'eau
        square = terrain.get_square(water_position)
        if not square or square.terrain_type != Square.TYPE_WATER:
            return 0
            
        # Boire de l'eau (récupérer des points de soif)
        thirst_recovered = self.recover_thirst(WATER_THIRST_RECOVERY)
        return thirst_recovered 