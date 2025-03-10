"""
Module pour sérialiser et désérialiser l'état du jeu.
"""
import json
import pickle
from game.animal import Animal
from game.resources import Fruit, GreenFruit, RedFruit

class GameStateEncoder:
    """Classe pour encoder et décoder l'état du jeu"""
    
    @staticmethod
    def encode_game_state(game):
        """Encode l'état du jeu en un dictionnaire sérialisable
        
        Args:
            game: Instance de la classe Game
            
        Returns:
            dict: État du jeu sérialisable
        """
        try:
            state = {
                "current_turn": game.current_turn,
                "game_over": game.game_over,
                "winner": game.winner.name if game.winner else None,
                "animals": [],
                "resources": [],
                "players": []  # Liste des joueurs connectés
            }
            
            # Encoder les animaux
            for animal in game.animals:
                animal_data = {
                    "name": animal.name,
                    "max_hp": animal.max_hp,
                    "hp": animal.hp,
                    "max_stamina": animal.max_stamina,
                    "stamina": animal.stamina,
                    "speed": animal.speed,
                    "speed_points": animal.speed_points,
                    "position": animal.position,
                    "is_alive": animal.is_alive,
                    "teeth": animal.teeth,
                    "claws": animal.claws,
                    "skin": animal.skin,
                    "height": animal.height,
                    "max_hunger": animal.max_hunger,
                    "hunger": animal.hunger,
                    "max_thirst": animal.max_thirst,
                    "thirst": animal.thirst
                }
                state["animals"].append(animal_data)
                
                # Ajouter l'animal à la liste des joueurs
                player_data = {
                    "id": game.animals.index(animal) + 1,
                    "name": animal.name,
                    "ready": True  # Par défaut, les animaux sont prêts
                }
                state["players"].append(player_data)
            
            # Encoder les ressources
            for position, resource in game.terrain.resources.items():
                resource_data = {
                    "position": position,
                    "type": resource.__class__.__name__
                }
                
                # Ajouter des attributs spécifiques selon le type de ressource
                if isinstance(resource, Fruit):
                    resource_data.update({
                        "heal_amount": resource.heal_amount,
                        "stamina_recovery": resource.stamina_recovery,
                        "hunger_recovery": resource.hunger_recovery
                    })
                
                state["resources"].append(resource_data)
            
            # Encoder le terrain
            terrain_data = {
                "width": game.terrain.width,
                "height": game.terrain.height,
                "squares": []
            }
            
            # Encoder les cases du terrain
            for y in range(game.terrain.height):
                for x in range(game.terrain.width):
                    square = game.terrain.grid[y][x]
                    square_data = {
                        "x": square.x,
                        "y": square.y,
                        "terrain_type": square.terrain_type,
                        "is_orchard": square.is_orchard,
                        "speed_points": square.speed_points
                    }
                    terrain_data["squares"].append(square_data)
            
            state["terrain"] = terrain_data
            
            return state
        except Exception as e:
            print(f"Erreur lors de l'encodage de l'état du jeu: {e}")
            import traceback
            traceback.print_exc()
            # Retourner un état minimal en cas d'erreur
            return {
                "current_turn": 0,
                "game_over": False,
                "winner": None,
                "animals": [],
                "resources": [],
                "players": [],
                "terrain": {
                    "width": 10,
                    "height": 10,
                    "squares": []
                },
                "error": str(e)
            }
    
    @staticmethod
    def decode_game_state(state, game):
        """Décode l'état du jeu à partir d'un dictionnaire
        
        Args:
            state: Dictionnaire contenant l'état du jeu
            game: Instance de la classe Game à mettre à jour
            
        Returns:
            Game: Instance de la classe Game mise à jour
        """
        try:
            from game.game import Game
            from game.terrain import Terrain
            from game.square import Square
            
            # Vérifier que state est un dictionnaire
            if not isinstance(state, dict):
                print(f"Erreur: state n'est pas un dictionnaire mais {type(state)}")
                return game
            
            # Si l'état contient une erreur, l'afficher et retourner le jeu inchangé
            if "error" in state:
                print(f"Erreur dans l'état du jeu: {state['error']}")
                return game
            
            # Si l'état contient un indicateur de configuration terminée, le conserver
            setup_complete = state.get("setup_complete", False)
            
            # Si l'état contient un indicateur de démarrage de partie, le conserver
            game_started = state.get("game_started", False)
            
            # Conserver la liste des joueurs
            players = state.get("players", [])
            
            # Mettre à jour les attributs de base du jeu
            game.current_turn = state.get("current_turn", 0)
            game.game_over = state.get("game_over", False)
            
            # Recréer le terrain
            terrain_data = state.get("terrain", {})
            width = terrain_data.get("width", 10)
            height = terrain_data.get("height", 10)
            
            # Réinitialiser le terrain
            game.terrain = Terrain(width, height)
            
            # Mettre à jour les cases du terrain
            for square_data in terrain_data.get("squares", []):
                x = square_data.get("x", 0)
                y = square_data.get("y", 0)
                if 0 <= x < width and 0 <= y < height:
                    square = game.terrain.grid[y][x]
                    square.terrain_type = square_data.get("terrain_type", Square.TYPE_NORMAL)
                    square.is_orchard = square_data.get("is_orchard", False)
                    square.speed_points = square_data.get("speed_points", 0)
            
            # Réinitialiser les animaux
            game.animals = []
            
            # Recréer les animaux
            for animal_data in state.get("animals", []):
                animal = Animal(
                    name=animal_data.get("name", "Animal"),
                    hp=animal_data.get("max_hp", 10),
                    stamina=animal_data.get("max_stamina", 10),
                    speed=animal_data.get("speed", 5),
                    position=animal_data.get("position", 1),
                    teeth=animal_data.get("teeth", 1),
                    claws=animal_data.get("claws", 1),
                    skin=animal_data.get("skin", 1),
                    height=animal_data.get("height", 1)
                )
                
                # Mettre à jour les attributs variables
                animal.hp = animal_data.get("hp", animal.max_hp)
                animal.stamina = animal_data.get("stamina", animal.max_stamina)
                animal.speed_points = animal_data.get("speed_points", animal.speed)
                animal.is_alive = animal_data.get("is_alive", True)
                animal.hunger = animal_data.get("hunger", animal.max_hunger)
                animal.thirst = animal_data.get("thirst", animal.max_thirst)
                
                # Ajouter l'animal au jeu
                game.add_animal(animal, animal.position)
            
            # Recréer les ressources
            for resource_data in state.get("resources", []):
                position = resource_data.get("position", 1)
                resource_type = resource_data.get("type", "Fruit")
                
                # Créer la ressource selon son type
                if resource_type == "GreenFruit":
                    resource = GreenFruit(position)
                elif resource_type == "RedFruit":
                    resource = RedFruit(position)
                else:
                    # Fruit générique
                    resource = Fruit(
                        name="Fruit",
                        heal_amount=resource_data.get("heal_amount", 5),
                        stamina_recovery=resource_data.get("stamina_recovery", 2),
                        hunger_recovery=resource_data.get("hunger_recovery", 20),
                        position=position
                    )
                
                # Ajouter la ressource au jeu
                game.add_resource(resource, position)
            
            # Mettre à jour le gagnant si la partie est terminée
            if game.game_over:
                winner_name = state.get("winner")
                if winner_name:
                    for animal in game.animals:
                        if animal.name == winner_name:
                            game.winner = animal
                            break
            
            # Restaurer les indicateurs
            state["setup_complete"] = setup_complete
            state["game_started"] = game_started
            state["players"] = players
            
            return game
        except Exception as e:
            print(f"Erreur lors du décodage de l'état du jeu: {e}")
            import traceback
            traceback.print_exc()
            return game 