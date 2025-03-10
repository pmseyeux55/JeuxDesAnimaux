class Display:
    def __init__(self, game):
        self.game = game

    def show_terrain(self):
        """Affiche le terrain de jeu"""
        terrain = self.game.terrain
        width, height = terrain.width, terrain.height
        
        print("+" + "-" * (width * 2 - 1) + "+")
        
        for y in range(height):
            line = "|"
            for x in range(width):
                position = terrain.coordinates_to_position(x, y)
                animal = terrain.get_animal_at(position)
                resource = terrain.get_resource_at(position)
                
                if animal:
                    line += animal.name[0] + " "  # Première lettre du nom de l'animal
                elif resource:
                    line += "F "  # F pour Fruit
                else:
                    line += ". "
            line = line[:-1] + "|"  # Remplacer le dernier espace par |
            print(line)
            
        print("+" + "-" * (width * 2 - 1) + "+")

    def show_animal_stats(self, animal):
        """Affiche les statistiques d'un animal"""
        print(f"Nom: {animal.name}")
        print(f"HP: {animal.hp}/{animal.max_hp}")
        print(f"Stamina: {animal.stamina}/{animal.max_stamina}")
        print(f"Vitesse: {animal.speed} (Points: {animal.speed_points})")
        print(f"Position: {animal.position}")
        print(f"Statut: {'Vivant' if animal.is_alive else 'Mort'}")

    def show_game_status(self):
        """Affiche le statut du jeu"""
        print(f"Tour actuel: {self.game.current_turn}")
        print(f"Nombre d'animaux: {len(self.game.animals)}")
        print(f"Jeu terminé: {'Oui' if self.game.game_over else 'Non'}")
        if self.game.winner:
            print(f"Gagnant: {self.game.winner.name}")

    def show_possible_actions(self, animal):
        """Affiche les actions possibles pour un animal"""
        actions = self.game.get_animal_possible_actions(animal)
        
        if not actions:
            print(f"{animal.name} ne peut effectuer aucune action.")
            return
            
        print(f"Actions possibles pour {animal.name}:")
        
        if "walk" in actions:
            print("Walk vers les positions:", actions["walk"])
            
        if "run" in actions:
            print("Run vers les positions:", actions["run"])
            
        if "bite" in actions:
            print("Bite les animaux:", [a.name for a in actions["bite"]])
            
        if "slap" in actions:
            print("Slap les animaux:", [a.name for a in actions["slap"]]) 