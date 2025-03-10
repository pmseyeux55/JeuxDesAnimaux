from game.terrain import Terrain
from game.resources import Fruit, GreenFruit, RedFruit
from game.square import Square
from game.config import (
    TERRAIN_WIDTH, TERRAIN_HEIGHT,
    BITE_COST, SLAP_COST,
    RUN_COST
)
import random

class Game:
    def __init__(self, terrain_width=TERRAIN_WIDTH, terrain_height=TERRAIN_HEIGHT):
        self.terrain = Terrain(terrain_width, terrain_height)
        self.animals = []
        self.current_turn = 0
        self.game_over = False
        self.winner = None

    def add_animal(self, animal, position):
        """Ajoute un animal au jeu"""
        if self.terrain.place_animal(animal, position):
            self.animals.append(animal)
            return True
        return False

    def add_resource(self, resource, position):
        """Ajoute une ressource au jeu"""
        return self.terrain.place_resource(resource, position)

    def get_next_animal_to_play(self):
        """Détermine quel animal doit jouer en fonction des points de vitesse"""
        if not self.animals or self.game_over:
            return None

        # Trouver l'animal avec le plus de points de vitesse
        animals_alive = [animal for animal in self.animals if animal.is_alive]
        if not animals_alive:
            self.game_over = True
            return None
            
        # Si un seul animal est en vie, c'est le gagnant
        if len(animals_alive) == 1:
            self.game_over = True
            self.winner = animals_alive[0]
            return None
            
        # Trouver l'animal avec le plus de points de vitesse
        next_animal = max(animals_alive, key=lambda a: a.speed_points)
        
        # Si l'animal a au moins 100 points de vitesse, il peut jouer
        if next_animal.speed_points >= 100:
            # Ne pas déduire les points de vitesse ici, cela sera fait dans play_turn
            return next_animal
            
        # Sinon, ajouter des points de vitesse à tous les animaux
        for animal in animals_alive:
            animal.add_speed_points(animal.speed)
            
        # Mettre à jour les points de vitesse des cases en même temps
        # Passer True pour indiquer que les cases doivent gagner des points de vitesse
        new_fruit_positions = self.update_terrain(add_speed=True)
        
        # Vérifier à nouveau si un animal peut jouer
        next_animal = max(animals_alive, key=lambda a: a.speed_points)
        if next_animal.speed_points >= 100:
            # Ne pas déduire les points de vitesse ici, cela sera fait dans play_turn
            return next_animal
            
        # Aucun animal ne peut jouer pour l'instant
        return None

    def play_turn(self, animal, action, *args):
        """Joue un tour pour un animal"""
        if animal not in self.animals or not animal.is_alive:
            return False
            
        # Vérifier si l'animal a assez de points de vitesse
        if animal.speed_points < 100:
            return False
            
        # Déduire les points de vitesse pour jouer un tour
        animal.use_speed_points(100)
            
        result = False
        fruit_consumed = False
        
        # Exécuter l'action
        if action == "walk":
            if len(args) == 1 and animal.walk(args[0], self.terrain):
                # La méthode move_animal retourne maintenant un tuple (success, effects)
                success, effects = self.terrain.move_animal(animal, args[0])
                if success:
                    result = True
                    # Vérifier si un fruit a été consommé (via les effets de la case)
                    if "heal" in effects or "stamina" in effects:
                        fruit_consumed = True
                
        elif action == "run":
            if len(args) == 1 and animal.run(args[0], self.terrain):
                # La méthode move_animal retourne maintenant un tuple (success, effects)
                success, effects = self.terrain.move_animal(animal, args[0])
                if success:
                    result = True
                    # Vérifier si un fruit a été consommé (via les effets de la case)
                    if "heal" in effects or "stamina" in effects:
                        fruit_consumed = True
                
        elif action == "bite":
            if len(args) == 1 and isinstance(args[0], type(animal)):
                damage = animal.bite(args[0], self.terrain)
                if damage > 0:
                    result = True
                    
        elif action == "slap":
            if len(args) == 1 and isinstance(args[0], type(animal)):
                damage = animal.slap(args[0], self.terrain)
                if damage > 0:
                    result = True
        
        elif action == "drink":
            if len(args) == 1:
                thirst_recovered = animal.drink(args[0], self.terrain)
                if thirst_recovered > 0:
                    result = True
        
        # Vérifier si un animal est mort
        for a in self.animals:
            if not a.is_alive:
                # Retirer l'animal mort du terrain
                self.terrain.remove_animal(a)
                
        # Vérifier si le jeu est terminé
        self.check_game_over()
        
        # Vérifier si des fruits peuvent être générés (sans ajouter de points de vitesse aux cases)
        if result:
            self.update_terrain(add_speed=False)
        
        # Retourner le résultat et si un fruit a été consommé
        return (result, fruit_consumed) if result else False

    def check_game_over(self):
        """Vérifie si la partie est terminée"""
        animals_alive = [animal for animal in self.animals if animal.is_alive]
        
        if len(animals_alive) <= 1:
            self.game_over = True
            if animals_alive:
                self.winner = animals_alive[0]
            return True
            
        return False

    def get_animal_possible_actions(self, animal):
        """Retourne les actions possibles pour un animal"""
        if not animal.is_alive or animal.speed_points < 100:
            return {}
            
        actions = {}
        
        # Déplacements
        actions["walk"] = animal.get_possible_walk_positions(self.terrain)
        
        # Course (si assez de stamina)
        if animal.stamina >= RUN_COST:
            actions["run"] = animal.get_possible_run_positions(self.terrain)
            
        # Attaques
        if animal.stamina >= BITE_COST:
            # Trouver les animaux adjacents
            bite_targets = []
            for other_animal in self.animals:
                if other_animal != animal and other_animal.is_alive and self.terrain.is_adjacent(animal.position, other_animal.position):
                    bite_targets.append(other_animal)
            if bite_targets:
                actions["bite"] = bite_targets
                
        if animal.stamina >= SLAP_COST:
            # Même logique que pour bite
            slap_targets = []
            for other_animal in self.animals:
                if other_animal != animal and other_animal.is_alive and self.terrain.is_adjacent(animal.position, other_animal.position):
                    slap_targets.append(other_animal)
            if slap_targets:
                actions["slap"] = slap_targets
                
        # Action de boire
        # Trouver les cases d'eau adjacentes
        drink_targets = []
        for position in self.terrain.get_adjacent_positions(animal.position):
            square = self.terrain.get_square(position)
            if square and square.terrain_type == Square.TYPE_WATER:
                drink_targets.append(position)
        if drink_targets:
            actions["drink"] = drink_targets
                
        return actions
        
    def update_terrain(self, add_speed=True):
        """Met à jour le terrain (points de vitesse des cases, génération de fruits)
        
        Args:
            add_speed: Si True, ajoute des points de vitesse aux cases
            
        Returns:
            list: Liste des positions où des fruits ont été générés
        """
        # Choisir aléatoirement entre les deux types de fruits
        fruit_class = random.choice([GreenFruit, RedFruit])
        
        return self.terrain.update_squares(fruit_class, add_speed) 