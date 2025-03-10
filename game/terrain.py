from game.config import TERRAIN_WIDTH, TERRAIN_HEIGHT, GREEN_FRUIT_POSITIONS, RED_FRUIT_POSITIONS, LION_START_POSITION, TIGER_START_POSITION
from game.square import Square

class Terrain:
    def __init__(self, width=TERRAIN_WIDTH, height=TERRAIN_HEIGHT):
        self.width = width
        self.height = height
        # Initialiser la grille avec des objets Square
        self.grid = [[Square(x, y) for x in range(width)] for y in range(height)]
        # Garder ces dictionnaires pour un accès rapide
        self.resources = {}  # {position: Resource}
        self.animals = {}  # {position: Animal}
        
        # Marquer les cases qui peuvent produire des fruits (vergers)
        for position in GREEN_FRUIT_POSITIONS:
            square = self.get_square(position)
            if square:
                square.is_orchard = True
        for position in RED_FRUIT_POSITIONS:
            square = self.get_square(position)
            if square:
                square.is_orchard = True
        
        # Initialiser les tuiles d'eau dans le carré central
        self.initialize_water_tiles()

    def initialize_water_tiles(self):
        """Initialise les tuiles d'eau uniquement sur les bords du carré central de 6x6, des cases 23 à 78"""
        import random
        
        # Définir les limites du carré central (6x6)
        start_row = 2  # Ligne 2 (position 21-30)
        end_row = 7    # Ligne 7 (position 71-80)
        start_col = 2  # Colonne 2 (positions 3, 13, 23, etc.)
        end_col = 7    # Colonne 7 (positions 8, 18, 28, etc.)
        
        # Nombre de tuiles d'eau à créer (environ 20% du carré central)
        num_water_tiles = 10  # Augmenté pour avoir plus de tuiles d'eau sur les bords
        
        # Positions à éviter (positions de départ des animaux et positions des fruits)
        avoid_positions = [LION_START_POSITION, TIGER_START_POSITION] + GREEN_FRUIT_POSITIONS + RED_FRUIT_POSITIONS
        
        # Créer les tuiles d'eau uniquement sur les bords du carré central
        water_tiles_created = 0
        while water_tiles_created < num_water_tiles:
            # Choisir une position aléatoire sur les bords du carré central
            # Pour cela, on choisit d'abord si on veut une position sur un bord horizontal ou vertical
            if random.choice([True, False]):
                # Bord horizontal (haut ou bas)
                row = random.choice([start_row, end_row])
                col = random.randint(start_col, end_col)
            else:
                # Bord vertical (gauche ou droite)
                row = random.randint(start_row, end_row)
                col = random.choice([start_col, end_col])
            
            position = self.coordinates_to_position(col, row)
            
            # Vérifier que la position n'est pas à éviter
            if position not in avoid_positions:
                square = self.get_square(position)
                if square and square.terrain_type == Square.TYPE_NORMAL:
                    # Définir la case comme une tuile d'eau
                    square.terrain_type = Square.TYPE_WATER
                    water_tiles_created += 1
                    # Ajouter la position à la liste des positions à éviter pour éviter les doublons
                    avoid_positions.append(position)

    def position_to_coordinates(self, position):
        """Convertit une position (1-100) en coordonnées (x, y)"""
        position -= 1  # Ajustement car les positions commencent à 1
        x = position % self.width
        y = position // self.width
        return x, y

    def coordinates_to_position(self, x, y):
        """Convertit des coordonnées (x, y) en position (1-100)"""
        return y * self.width + x + 1
    
    def get_square(self, position):
        """Récupère l'objet Square à une position donnée"""
        if not self.is_valid_position(position):
            return None
        x, y = self.position_to_coordinates(position)
        return self.grid[y][x]

    def is_valid_position(self, position):
        """Vérifie si une position est valide"""
        return 1 <= position <= self.width * self.height

    def is_occupied(self, position):
        """Vérifie si une position est occupée par un animal"""
        square = self.get_square(position)
        return square and square.is_occupied

    def is_valid_move(self, from_pos, to_pos, distance=1):
        """Vérifie si un déplacement est valide (sans diagonales)"""
        if not self.is_valid_position(to_pos):
            return False
            
        # Vérifier si la case de destination peut être occupée
        to_square = self.get_square(to_pos)
        if not to_square or not to_square.can_move_to(None):  # None sera remplacé par l'animal plus tard
            return False

        from_x, from_y = self.position_to_coordinates(from_pos)
        to_x, to_y = self.position_to_coordinates(to_pos)

        # Calculer la distance de Manhattan
        manhattan_distance = abs(to_x - from_x) + abs(to_y - from_y)
        
        # Vérifier si le déplacement est horizontal ou vertical (pas de diagonale)
        is_horizontal_or_vertical = (from_x == to_x) or (from_y == to_y)
        
        return manhattan_distance <= distance and is_horizontal_or_vertical

    def is_adjacent(self, pos1, pos2):
        """Vérifie si deux positions sont adjacentes (sans diagonales)"""
        if not self.is_valid_position(pos1) or not self.is_valid_position(pos2):
            return False
            
        pos1_x, pos1_y = self.position_to_coordinates(pos1)
        pos2_x, pos2_y = self.position_to_coordinates(pos2)
        
        # Calculer la distance de Manhattan
        manhattan_distance = abs(pos2_x - pos1_x) + abs(pos2_y - pos1_y)
        
        # Vérifier si les positions sont adjacentes horizontalement ou verticalement
        return manhattan_distance == 1

    def get_adjacent_positions(self, position):
        """Retourne toutes les positions adjacentes à une position donnée"""
        if not self.is_valid_position(position):
            return []
            
        x, y = self.position_to_coordinates(position)
        adjacent_positions = []
        
        # Vérifier les quatre directions (haut, bas, gauche, droite)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                new_position = self.coordinates_to_position(new_x, new_y)
                adjacent_positions.append(new_position)
                
        return adjacent_positions

    def get_valid_moves(self, position, distance=1):
        """Retourne toutes les positions valides où un animal peut se déplacer"""
        if not self.is_valid_position(position):
            return []
        
        valid_moves = []
        x, y = self.position_to_coordinates(position)
        animal = self.get_animal_at(position)
        
        # Si distance = 1, on cherche les cases adjacentes (sans diagonales)
        if distance == 1:
            # Vérifier les 4 directions (horizontales et verticales uniquement)
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Haut, Droite, Bas, Gauche
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    new_position = self.coordinates_to_position(new_x, new_y)
                    square = self.get_square(new_position)
                    if square and square.can_move_to(animal):
                        valid_moves.append(new_position)
        # Si distance > 1, on cherche les cases à exactement cette distance (sans diagonales)
        else:
            # Parcourir toutes les cases dans un carré de côté 2*distance+1
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    # Calculer la distance de Manhattan
                    manhattan_distance = abs(dx) + abs(dy)
                    # Vérifier si la case est exactement à la distance spécifiée et n'est pas en diagonale
                    if manhattan_distance == distance and (dx == 0 or dy == 0):
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.width and 0 <= new_y < self.height:
                            new_position = self.coordinates_to_position(new_x, new_y)
                            square = self.get_square(new_position)
                            if square and square.can_move_to(animal):
                                valid_moves.append(new_position)
        
        return valid_moves

    def place_animal(self, animal, position):
        """Place un animal sur le terrain"""
        square = self.get_square(position)
        if square and square.place_animal(animal):
            self.animals[position] = animal
            return True
        return False

    def move_animal(self, animal, new_position):
        """Déplace un animal sur le terrain"""
        # Vérifier si l'animal est bien à sa position actuelle
        if animal.position in self.animals and self.animals[animal.position] == animal:
            old_position = animal.position
            old_square = self.get_square(old_position)
            new_square = self.get_square(new_position)
            
            # Retirer l'animal de sa position actuelle
            if old_square:
                old_square.remove_animal()
                del self.animals[old_position]
            
            # Placer l'animal à sa nouvelle position
            if new_square and new_square.place_animal(animal):
                self.animals[new_position] = animal
                
                # Appliquer les effets de la nouvelle case
                effects = new_square.on_enter(animal)
                
                return True, effects
            
            # Si le placement échoue, remettre l'animal à sa position d'origine
            if old_square:
                old_square.place_animal(animal)
                self.animals[old_position] = animal
                
        return False, {}

    def place_resource(self, resource, position):
        """Place une ressource sur le terrain"""
        square = self.get_square(position)
        if square and square.place_resource(resource):
            self.resources[position] = resource
            return True
        return False

    def remove_resource(self, position):
        """Retire une ressource du terrain"""
        square = self.get_square(position)
        if square and square.has_resource:
            resource = square.remove_resource()
            if position in self.resources:
                del self.resources[position]
            return resource
        return None

    def get_resource_at(self, position):
        """Récupère une ressource à une position donnée"""
        square = self.get_square(position)
        return square.resource if square else None

    def get_animal_at(self, position):
        """Récupère un animal à une position donnée"""
        square = self.get_square(position)
        return square.animal if square else None

    def remove_animal(self, animal):
        """Retire un animal du terrain"""
        if animal.position in self.animals and self.animals[animal.position] == animal:
            square = self.get_square(animal.position)
            if square:
                square.remove_animal()
            del self.animals[animal.position]
            return True
        return False
        
    def generate_fruit(self, fruit_class, probability=0.05):
        """Génère aléatoirement des fruits sur le terrain
        
        Args:
            fruit_class: Classe de fruit à générer
            probability: Probabilité de générer un fruit sur une case vide (0-1)
            
        Returns:
            list: Liste des positions où des fruits ont été générés
        """
        import random
        
        new_fruit_positions = []
        
        for y in range(self.height):
            for x in range(self.width):
                square = self.grid[y][x]
                position = square.position
                
                # Vérifier si la case est vide (pas d'animal ni de ressource)
                if not square.is_occupied and not square.has_resource:
                    # Générer un fruit avec la probabilité donnée
                    if random.random() < probability:
                        # Créer un nouveau fruit
                        fruit = fruit_class(position=position)
                        
                        # Placer le fruit sur la case
                        if square.place_resource(fruit):
                            self.resources[position] = fruit
                            new_fruit_positions.append(position)
        
        return new_fruit_positions
        
    def get_terrain_type_at(self, position):
        """Récupère le type de terrain à une position donnée"""
        square = self.get_square(position)
        return square.terrain_type if square else None
        
    def set_terrain_type(self, position, terrain_type):
        """Définit le type de terrain à une position donnée"""
        square = self.get_square(position)
        if square:
            square.terrain_type = terrain_type
            return True
        return False
        
    def update_squares(self, fruit_class, add_speed=True):
        """Met à jour les cases du terrain (points de vitesse, génération de fruits)
        
        Args:
            fruit_class: Classe de fruit à générer
            add_speed: Si True, ajoute des points de vitesse aux cases
            
        Returns:
            list: Liste des positions où des fruits ont été générés
        """
        new_fruit_positions = []
        
        # Compter les cases qui ont atteint 100 points de vitesse
        ready_squares = 0
        
        for y in range(self.height):
            for x in range(self.width):
                square = self.grid[y][x]
                position = square.position
                
                # Ajouter des points de vitesse si demandé
                if add_speed:
                    square_ready = square.add_speed_points()
                else:
                    square_ready = square.speed_points >= 100
                
                # Si la case a atteint 100 points de vitesse
                if square_ready:
                    ready_squares += 1
                    
                    # Essayer de générer un fruit
                    if square.try_generate_fruit(fruit_class):
                        # Mettre à jour le dictionnaire des ressources
                        self.resources[position] = square.resource
                        new_fruit_positions.append(position)
        
        # Afficher le nombre de cases prêtes à générer des fruits
        # if ready_squares > 0:
        #     print(f"{ready_squares} cases ont atteint 100 points de vitesse")
        
        return new_fruit_positions