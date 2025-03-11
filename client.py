#!/usr/bin/env python3
"""
Script pour lancer un client de jeu des animaux.
"""
import sys
import argparse
import pygame
import time
import traceback
from network.client import GameClient
from game.game import Game
from ui.gui import GUI
from network.game_state import GameStateEncoder

class NetworkedGUI(GUI):
    """Interface graphique pour le jeu en réseau"""
    
    def __init__(self, game, client):
        """Initialise l'interface graphique
        
        Args:
            game: Instance de la classe Game
            client: Instance de la classe GameClient
        """
        print("Initialisation de NetworkedGUI...")
        super().__init__(game)
        self.client = client
        self.player_id = None
        self.is_my_turn = False
        self.last_action_time = 0
        self.setup_complete = False
        self.opponent_setup_complete = False
        self.connection_error = False
        
        print("Enregistrement des callbacks...")
        # Enregistrer les callbacks pour les événements réseau
        self.client.register_callback("connection", self.on_connection)
        self.client.register_callback("game_start", self.on_game_start)
        self.client.register_callback("game_update", self.on_game_update)
        self.client.register_callback("disconnect", self.on_disconnect)
        
        # Ajouter un message d'attente
        self.waiting_message = "En attente d'un autre joueur..."
        self.show_info_message(self.waiting_message, duration=float('inf'))
        print("NetworkedGUI initialisé avec succès")
    
    def on_connection(self, client_id):
        """Callback appelé lorsque la connexion est établie
        
        Args:
            client_id: ID du client
        """
        print(f"Callback on_connection appelé avec ID {client_id}")
        self.player_id = client_id
        print(f"Connecté au serveur avec l'ID {client_id}")
        
        # Mettre à jour le message d'attente
        self.waiting_message = f"Connecté en tant que joueur {client_id}. En attente d'un autre joueur..."
        self.show_info_message(self.waiting_message, duration=float('inf'))
    
    def on_game_start(self):
        """Callback appelé lorsque la partie commence"""
        print("Callback on_game_start appelé")
        print("La partie commence")
        
        # Effacer le message d'attente
        self.info_message = ""
        self.info_message_duration = 0
        
        # Vérifier que le client est toujours connecté
        if not self.client.connected:
            print("Client déconnecté lors du démarrage de la partie, tentative de reconnexion...")
            reconnection_attempts = 0
            max_reconnection_attempts = 5
            
            while reconnection_attempts < max_reconnection_attempts:
                reconnection_attempts += 1
                print(f"Tentative de reconnexion {reconnection_attempts}/{max_reconnection_attempts}...")
                
                if self.client.reconnect():
                    print("Reconnexion réussie!")
                    break
                
                # Attendre avant la prochaine tentative
                time.sleep(2)
            
            if not self.client.connected:
                print("Impossible de se reconnecter au serveur après plusieurs tentatives")
                self.show_info_message("Impossible de se connecter au serveur. Appuyez sur Échap pour quitter.", duration=float('inf'))
                self.connection_error = True
                return
        
        # Afficher un message pour indiquer que le joueur doit configurer son animal
        self.show_info_message("Configurez votre animal", duration=120)
    
    def on_game_update(self, game_state):
        """Callback appelé lorsque l'état du jeu est mis à jour
        
        Args:
            game_state: Nouvel état du jeu
        """
        print(f"Callback on_game_update appelé avec état: {game_state.keys() if isinstance(game_state, dict) else 'non dict'}")
        try:
            # Si nous n'avons pas encore terminé notre configuration, ignorer les mises à jour
            if not self.setup_complete:
                print("Configuration non terminée, vérification de l'état de l'adversaire...")
                # Vérifier si l'adversaire a terminé sa configuration
                if isinstance(game_state, dict) and "setup_complete" in game_state and game_state["setup_complete"] == True:
                    print("L'adversaire a terminé sa configuration")
                    self.opponent_setup_complete = True
                    self.show_info_message("L'adversaire a terminé sa configuration. À vous de configurer votre animal.", duration=120)
                return
                
            print("Mise à jour de l'état du jeu...")
            
            # Sauvegarder notre animal avant la mise à jour
            our_animal = None
            if self.game.animals and len(self.game.animals) > 0:
                # Trouver notre animal en fonction de notre ID
                for animal in self.game.animals:
                    if self.game.animals.index(animal) + 1 == self.player_id:
                        our_animal = animal
                        break
            
            # Mettre à jour le jeu avec le nouvel état
            GameStateEncoder.decode_game_state(game_state, self.game)
            
            # Si nous avions un animal et qu'il a été remplacé, le restaurer
            if our_animal and self.game.animals:
                # Vérifier si notre animal est toujours dans la liste
                our_animal_found = False
                for animal in self.game.animals:
                    if self.game.animals.index(animal) + 1 == self.player_id:
                        our_animal_found = True
                        break
                
                # Si notre animal n'est plus dans la liste, l'ajouter
                if not our_animal_found:
                    self.game.add_animal(our_animal, our_animal.position)
            
            # Mettre à jour l'animal actuel
            self.current_animal = self.game.get_next_animal_to_play()
            
            # Déterminer si c'est notre tour
            animal_index = self.game.animals.index(self.current_animal) if self.current_animal in self.game.animals else -1
            self.is_my_turn = (animal_index + 1) == self.player_id
            
            # Afficher un message
            if self.is_my_turn:
                self.show_info_message("C'est votre tour", duration=120)
            else:
                self.show_info_message("En attente du tour de l'adversaire", duration=120)
        except Exception as e:
            print(f"Erreur lors de la mise à jour du jeu: {e}")
            traceback.print_exc()
            self.show_info_message(f"Erreur: {str(e)}", duration=120)
    
    def on_disconnect(self):
        """Callback appelé lorsque la connexion est perdue"""
        print("Callback on_disconnect appelé")
        print("Déconnecté du serveur")
        
        # Tenter de se reconnecter automatiquement
        print("Tentative de reconnexion automatique...")
        reconnection_attempts = 0
        max_reconnection_attempts = 3
        
        while reconnection_attempts < max_reconnection_attempts:
            reconnection_attempts += 1
            print(f"Tentative de reconnexion {reconnection_attempts}/{max_reconnection_attempts}...")
            
            if self.client.reconnect():
                print("Reconnexion réussie!")
                self.show_info_message("Reconnecté au serveur", duration=120)
                return
            
            # Attendre avant la prochaine tentative
            time.sleep(2)
        
        # Si toutes les tentatives ont échoué
        self.connection_error = True
        self.show_info_message("Impossible de se reconnecter au serveur. Appuyez sur Échap pour quitter.", duration=float('inf'))
        self.running = False
    
    def handle_click(self, pos, shift_pressed=False):
        """Gère les clics sur le terrain
        
        Args:
            pos: Position du clic (x, y)
            shift_pressed: True si la touche Shift est enfoncée, False sinon
        """
        # Si nous n'avons pas encore terminé notre configuration, ignorer les clics
        if not self.setup_complete:
            print("Configuration non terminée, clic ignoré")
            return
            
        # Si ce n'est pas notre tour, ignorer le clic
        if not self.is_my_turn:
            self.show_info_message("Ce n'est pas votre tour", duration=60)
            return
        
        # Limiter la fréquence des actions (éviter les clics multiples)
        current_time = time.time()
        if current_time - self.last_action_time < 0.5:  # 500 ms entre chaque action
            return
        
        try:
            # Appeler la méthode de la classe parente
            super().handle_click(pos, shift_pressed)
            
            # Mettre à jour le temps de la dernière action
            self.last_action_time = current_time
            
            # Envoyer l'état du jeu au serveur
            game_state = GameStateEncoder.encode_game_state(self.game)
            self.client.send_action(game_state)
            
            # Mettre à jour le statut du tour
            self.is_my_turn = False
            self.show_info_message("En attente du tour de l'adversaire", duration=120)
        except Exception as e:
            print(f"Erreur lors du traitement du clic: {e}")
            traceback.print_exc()
            self.show_info_message(f"Erreur: {str(e)}", duration=120)
    
    def run(self):
        """Exécute la boucle principale du jeu"""
        try:
            super().run()
        except Exception as e:
            print(f"Erreur dans la boucle principale: {e}")
            traceback.print_exc()
            
        # Si la connexion a été perdue, afficher un message et attendre que l'utilisateur quitte
        if self.connection_error:
            print("Connexion perdue, attente de la fermeture par l'utilisateur...")
            try:
                # Vérifier que pygame est toujours initialisé
                if not pygame.get_init():
                    pygame.init()
                
                # Vérifier que le module font est initialisé
                if not pygame.font.get_init():
                    pygame.font.init()
                
                screen = pygame.display.get_surface()
                if screen is None:
                    screen = pygame.display.set_mode((800, 600))
                
                font = pygame.font.SysFont(None, 36)
                text = font.render("Connexion perdue. Appuyez sur Échap pour quitter.", True, (255, 0, 0))
                text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            waiting = False
                    
                    screen.fill((0, 0, 0))
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    pygame.time.delay(100)
            except Exception as e:
                print(f"Erreur lors de l'affichage du message de déconnexion: {e}")
                traceback.print_exc()
    
    def setup_complete_callback(self, game):
        """Callback appelé lorsque la configuration est terminée
        
        Args:
            game: Instance de la classe Game configurée
        """
        print("Callback setup_complete_callback appelé")
        try:
            # Mettre à jour le jeu
            # Conserver uniquement notre animal et les ressources
            if self.game.animals:
                # Supprimer tous les animaux
                for animal in list(self.game.animals):
                    self.game.terrain.remove_animal(animal)
                self.game.animals = []
            
            # Ajouter notre animal au jeu
            if game.animals and len(game.animals) > 0:
                our_animal = game.animals[0]  # Dans le mode multijoueur, il n'y a qu'un seul animal
                self.game.add_animal(our_animal, our_animal.position)
            
            # Marquer la configuration comme terminée
            self.setup_complete = True
            print("Configuration terminée, envoi de l'état au serveur...")
            
            # Envoyer l'état du jeu au serveur avec un indicateur de configuration terminée
            game_state = GameStateEncoder.encode_game_state(self.game)
            game_state["setup_complete"] = True
            self.client.send_action(game_state)
            
            # Si l'adversaire a également terminé sa configuration, commencer la partie
            if self.opponent_setup_complete:
                print("L'adversaire a également terminé sa configuration, début de la partie")
                # Déterminer si c'est notre tour
                self.current_animal = self.game.get_next_animal_to_play()
                animal_index = self.game.animals.index(self.current_animal) if self.current_animal in self.game.animals else -1
                self.is_my_turn = (animal_index + 1) == self.player_id
                
                # Afficher un message
                if self.is_my_turn:
                    self.show_info_message("C'est votre tour", duration=120)
                else:
                    self.show_info_message("En attente du tour de l'adversaire", duration=120)
            else:
                print("En attente que l'adversaire termine sa configuration...")
                # Afficher un message d'attente
                self.show_info_message("En attente que l'adversaire termine sa configuration...", duration=float('inf'))
        except Exception as e:
            print(f"Erreur lors de la finalisation de la configuration: {e}")
            traceback.print_exc()
            self.show_info_message(f"Erreur: {str(e)}", duration=120)

def main():
    """Fonction principale"""
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description="Client de jeu des animaux")
    parser.add_argument("--host", default="localhost", help="Adresse IP du serveur (par défaut: localhost)")
    parser.add_argument("--port", type=int, default=5555, help="Port du serveur (par défaut: 5555)")
    args = parser.parse_args()
    
    # Se connecter au serveur
    client = GameClient(args.host, args.port)
    if not client.connect():
        print(f"Impossible de se connecter au serveur {args.host}:{args.port}")
        sys.exit(1)
    
    print(f"Connecté au serveur {args.host}:{args.port}")
    
    # Initialiser pygame
    pygame.init()
    
    # Créer le jeu
    game = Game()
    
    # Créer l'interface graphique
    gui = NetworkedGUI(game, client)
    
    # Lancer l'interface graphique
    gui.run()
    
    # Déconnecter le client
    client.disconnect()
    
    # Quitter pygame
    pygame.quit()

if __name__ == "__main__":
    main() 