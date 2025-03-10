"""
Module serveur pour le jeu des animaux.
Gère la connexion des clients et la synchronisation du jeu.
"""
import socket
import threading
import pickle
import json
import time
import traceback

class GameServer:
    """Serveur de jeu pour le jeu des animaux"""
    
    def __init__(self, host='0.0.0.0', port=5555):
        """Initialise le serveur
        
        Args:
            host: Adresse IP du serveur (0.0.0.0 pour écouter sur toutes les interfaces)
            port: Port d'écoute du serveur
        """
        print(f"Initialisation du serveur sur {host}:{port}")
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # Liste des connexions clients
        self.game_state = {}  # État du jeu à synchroniser
        self.running = False
        self.lock = threading.Lock()  # Verrou pour l'accès concurrent à game_state
        
    def start(self):
        """Démarre le serveur"""
        print("Création du socket serveur...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            print(f"Liaison du socket à {self.host}:{self.port}...")
            self.server_socket.bind((self.host, self.port))
            print("Mise en écoute du socket...")
            self.server_socket.listen(2)  # Maximum 2 joueurs
            self.running = True
            print(f"Serveur démarré sur {self.host}:{self.port}")
            
            # Démarrer le thread d'acceptation des connexions
            print("Démarrage du thread d'acceptation des connexions...")
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            print("Thread d'acceptation des connexions démarré")
            
            return True
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")
            traceback.print_exc()
            return False
    
    def stop(self):
        """Arrête le serveur"""
        print("Arrêt du serveur...")
        self.running = False
        
        # Fermer toutes les connexions clients
        print(f"Fermeture de {len(self.clients)} connexions clients...")
        for client in self.clients:
            try:
                client["socket"].close()
                print(f"Connexion client {client['address']} fermée")
            except Exception as e:
                print(f"Erreur lors de la fermeture de la connexion client {client['address']}: {e}")
        
        # Fermer le socket serveur
        if self.server_socket:
            print("Fermeture du socket serveur...")
            self.server_socket.close()
            
        print("Serveur arrêté")
    
    def accept_connections(self):
        """Accepte les connexions entrantes"""
        print("Début de l'acceptation des connexions...")
        while self.running:
            try:
                print("En attente d'une nouvelle connexion...")
                client_socket, address = self.server_socket.accept()
                print(f"Nouvelle connexion de {address}")
                
                # Créer un dictionnaire pour stocker les informations du client
                client_info = {
                    "socket": client_socket,
                    "address": address,
                    "id": len(self.clients) + 1  # ID du client (1 ou 2)
                }
                
                # Ajouter le client à la liste
                self.clients.append(client_info)
                print(f"Client ajouté avec ID {client_info['id']}")
                
                # Envoyer l'ID au client
                print(f"Envoi de l'ID {client_info['id']} au client...")
                self.send_to_client(client_socket, {"type": "connection", "id": client_info["id"]})
                
                # Démarrer un thread pour gérer ce client
                print(f"Démarrage du thread de gestion pour le client {address}...")
                client_thread = threading.Thread(target=self.handle_client, args=(client_info,))
                client_thread.daemon = True
                client_thread.start()
                print(f"Thread de gestion démarré pour le client {address}")
                
                # Si nous avons 2 joueurs, démarrer la partie
                if len(self.clients) == 2:
                    print("Deux joueurs connectés, démarrage de la partie...")
                    self.broadcast({"type": "game_start"})
                    print("Signal de démarrage de partie envoyé aux clients")
                
            except Exception as e:
                print(f"Erreur lors de l'acceptation d'une connexion: {e}")
                traceback.print_exc()
                if not self.running:
                    break
        
        print("Fin de l'acceptation des connexions")
    
    def handle_client(self, client_info):
        """Gère les messages d'un client
        
        Args:
            client_info: Dictionnaire contenant les informations du client
        """
        client_socket = client_info["socket"]
        client_address = client_info["address"]
        client_id = client_info["id"]
        
        print(f"Début de la gestion du client {client_address} (ID: {client_id})")
        
        while self.running:
            try:
                # Recevoir les données du client
                print(f"En attente de données du client {client_address}...")
                data = client_socket.recv(4096)
                if not data:
                    print(f"Aucune donnée reçue du client {client_address}, déconnexion")
                    break
                
                # Désérialiser les données
                print(f"Données reçues du client {client_address}, désérialisation...")
                message = pickle.loads(data)
                print(f"Message reçu du client {client_address}: {message.get('type', 'inconnu')}")
                
                # Traiter le message
                self.process_message(client_info, message)
                
            except Exception as e:
                print(f"Erreur lors de la gestion du client {client_address}: {e}")
                traceback.print_exc()
                break
        
        # Fermer la connexion
        try:
            print(f"Fermeture de la connexion avec le client {client_address}...")
            client_socket.close()
            print(f"Connexion avec le client {client_address} fermée")
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion avec le client {client_address}: {e}")
        
        # Retirer le client de la liste
        if client_info in self.clients:
            print(f"Suppression du client {client_address} de la liste...")
            self.clients.remove(client_info)
            print(f"Client {client_address} supprimé de la liste")
            
        print(f"Client {client_address} déconnecté")
    
    def process_message(self, client_info, message):
        """Traite un message reçu d'un client
        
        Args:
            client_info: Informations sur le client
            message: Message reçu
        """
        client_address = client_info["address"]
        client_id = client_info["id"]
        message_type = message.get("type")
        
        print(f"Traitement du message de type '{message_type}' du client {client_address} (ID: {client_id})")
        
        if message_type == "action":
            # Le client a effectué une action dans le jeu
            # Mettre à jour l'état du jeu
            print(f"Action reçue du client {client_address}, mise à jour de l'état du jeu...")
            with self.lock:
                # Mettre à jour l'état du jeu avec les données reçues
                action_data = message.get("data", {})
                self.game_state.update(action_data)
                print(f"État du jeu mis à jour avec les données du client {client_address}")
            
            # Diffuser la mise à jour à tous les clients
            print("Diffusion de la mise à jour à tous les clients...")
            self.broadcast({
                "type": "game_update",
                "data": self.game_state
            })
            print("Mise à jour diffusée à tous les clients")
        
        elif message_type == "chat":
            # Message de chat à diffuser à tous les clients
            print(f"Message de chat reçu du client {client_address}, diffusion...")
            self.broadcast({
                "type": "chat",
                "sender_id": client_info["id"],
                "message": message.get("message", "")
            })
            print("Message de chat diffusé à tous les clients")
    
    def broadcast(self, message):
        """Envoie un message à tous les clients
        
        Args:
            message: Message à envoyer
        """
        print(f"Diffusion d'un message de type '{message.get('type')}' à {len(self.clients)} clients...")
        for client in self.clients:
            self.send_to_client(client["socket"], message)
        print("Message diffusé à tous les clients")
    
    def send_to_client(self, client_socket, message):
        """Envoie un message à un client spécifique
        
        Args:
            client_socket: Socket du client
            message: Message à envoyer
        """
        try:
            # Sérialiser le message
            data = pickle.dumps(message)
            
            # Envoyer la taille des données suivie des données
            client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            client_socket.sendall(data)
        except Exception as e:
            print(f"Erreur lors de l'envoi d'un message: {e}")
            traceback.print_exc()
    
    def update_game_state(self, new_state):
        """Met à jour l'état du jeu
        
        Args:
            new_state: Nouvel état du jeu
        """
        print("Mise à jour de l'état du jeu...")
        with self.lock:
            self.game_state = new_state
            print("État du jeu mis à jour")
            
        # Diffuser la mise à jour à tous les clients
        print("Diffusion de la mise à jour à tous les clients...")
        self.broadcast({
            "type": "game_update",
            "data": self.game_state
        })
        print("Mise à jour diffusée à tous les clients")

# Fonction pour démarrer un serveur en mode autonome
def start_server(host='0.0.0.0', port=5555):
    """Démarre un serveur de jeu
    
    Args:
        host: Adresse IP du serveur
        port: Port d'écoute
        
    Returns:
        GameServer: Instance du serveur
    """
    print(f"Démarrage d'un serveur sur {host}:{port}...")
    server = GameServer(host, port)
    if server.start():
        print(f"Serveur démarré sur {host}:{port}")
        return server
    print("Échec du démarrage du serveur")
    return None

if __name__ == "__main__":
    # Démarrer le serveur en mode autonome
    print("Démarrage du serveur en mode autonome...")
    server = start_server()
    
    if server:
        try:
            # Garder le serveur en cours d'exécution
            print("Serveur en cours d'exécution, appuyez sur Ctrl+C pour arrêter...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Arrêter le serveur proprement
            print("Arrêt du serveur demandé par l'utilisateur...")
            server.stop()
            print("Serveur arrêté") 