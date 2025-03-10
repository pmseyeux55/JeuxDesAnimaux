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
        self.game_state = {"players": []}  # État du jeu à synchroniser avec une liste de joueurs vide
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
            self.server_socket.listen(5)
            self.running = True
            
            # Vérifier si le serveur est accessible depuis l'extérieur
            self.check_server_accessibility()
            
            # Démarrer le thread d'acceptation des connexions
            print("Démarrage du thread d'acceptation des connexions...")
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            print("Thread d'acceptation des connexions démarré")
            
            print(f"Serveur démarré sur {self.host}:{self.port}")
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
        print(f"Le serveur écoute sur {self.host}:{self.port}")
        if self.host == '0.0.0.0':
            print("Le serveur accepte les connexions de toutes les interfaces réseau")
            # Afficher les adresses IP disponibles pour aider à la connexion
            try:
                import socket
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                print(f"Adresse IP locale (hostname): {local_ip}")
                
                # Obtenir l'adresse IP externe (si disponible)
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    external_ip = s.getsockname()[0]
                    print(f"Adresse IP externe: {external_ip}")
                except Exception as e:
                    print(f"Impossible de déterminer l'adresse IP externe: {e}")
                finally:
                    s.close()
            except Exception as e:
                print(f"Erreur lors de la détermination des adresses IP: {e}")
        
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
                
                # Mettre à jour la liste des joueurs dans l'état du jeu
                with self.lock:
                    if "players" not in self.game_state:
                        self.game_state["players"] = []
                    
                    # Vérifier si le joueur existe déjà dans la liste
                    player_found = False
                    for player in self.game_state["players"]:
                        if player["id"] == client_info["id"]:
                            player_found = True
                            break
                    
                    # Ajouter seulement l'hôte (ID 1) automatiquement
                    if not player_found and client_info["id"] == 1:
                        self.game_state["players"].append({
                            "id": client_info["id"],
                            "name": "Hôte",
                            "ready": False
                        })
                
                # Envoyer l'ID au client
                print(f"Envoi de l'ID {client_info['id']} au client...")
                self.send_to_client(client_socket, {
                    "type": "connection",
                    "id": client_info["id"]
                })
                
                # Diffuser l'état du jeu mis à jour à tous les clients
                print("Diffusion de l'état du jeu mis à jour à tous les clients...")
                self.broadcast({
                    "type": "game_update",
                    "state": self.game_state
                })
                
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
        """Gère un client connecté
        
        Args:
            client_info: Informations sur le client
        """
        client_socket = client_info["socket"]
        client_address = client_info["address"]
        client_id = client_info["id"]
        
        print(f"Démarrage du gestionnaire pour le client {client_address} (ID: {client_id})")
        
        # Envoyer un message de bienvenue au client
        welcome_message = {
            "type": "connection",
            "id": client_id
        }
        self.send_to_client(client_socket, welcome_message)
        
        # Envoyer l'état actuel du jeu
        self.send_to_client(client_socket, {
            "type": "game_update",
            "state": self.game_state
        })
        
        # Boucle de réception des messages
        while self.running:
            try:
                # Recevoir la taille des données
                client_socket.settimeout(1)  # Timeout court pour pouvoir vérifier self.running régulièrement
                try:
                    size_bytes = client_socket.recv(4)
                    if not size_bytes:
                        print(f"Client {client_address} déconnecté (aucune donnée)")
                        break
                except socket.timeout:
                    # Timeout normal, continuer la boucle
                    continue
                except ConnectionResetError:
                    print(f"Connexion réinitialisée par le client {client_address}")
                    break
                except Exception as e:
                    print(f"Erreur lors de la réception de la taille des données du client {client_address}: {e}")
                    break
                
                # Remettre en mode bloquant pour la réception des données
                client_socket.settimeout(None)
                
                size = int.from_bytes(size_bytes, byteorder='big')
                print(f"Réception de {size} octets du client {client_address}")
                
                # Recevoir les données
                data = b""
                while len(data) < size:
                    try:
                        chunk = client_socket.recv(min(size - len(data), 4096))
                        if not chunk:
                            print(f"Client {client_address} déconnecté pendant la réception des données")
                            break
                        data += chunk
                    except Exception as e:
                        print(f"Erreur lors de la réception des données du client {client_address}: {e}")
                        break
                
                if len(data) < size:
                    # Données incomplètes, considérer le client comme déconnecté
                    break
                
                # Désérialiser les données
                try:
                    message = pickle.loads(data)
                    # Traiter le message
                    self.process_message(client_info, message)
                    
                    # Envoyer une confirmation de réception au client
                    # Cela permet de maintenir la connexion active et d'éviter les timeouts
                    ack_message = {
                        "type": "ack",
                        "message_type": message.get("type", "unknown")
                    }
                    self.send_to_client(client_socket, ack_message)
                    
                except Exception as e:
                    print(f"Erreur lors du traitement du message du client {client_address}: {e}")
                    traceback.print_exc()
            
            except Exception as e:
                print(f"Erreur générale lors de la gestion du client {client_address}: {e}")
                traceback.print_exc()
                break
        
        # Supprimer le client de la liste
        with self.lock:
            if client_info in self.clients:
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
                
                # Gérer le démarrage de la partie par l'hôte
                if "game_started" in action_data and client_id == 1:  # Seul l'hôte (ID 1) peut démarrer la partie
                    print(f"L'hôte a démarré la partie")
                    self.game_state["game_started"] = True
                    
                    # Informer tous les clients que la partie commence
                    print("Diffusion du signal de démarrage de partie à tous les clients...")
                    self.broadcast({"type": "game_start"})
                
                # Gérer le statut "prêt" du joueur
                if "ready" in action_data:
                    # Si le jeu n'a pas encore commencé, mettre à jour le statut du joueur
                    if not self.game_state.get("game_started", False):
                        # Initialiser la liste des joueurs si elle n'existe pas
                        if "players" not in self.game_state:
                            self.game_state["players"] = []
                        
                        # Mettre à jour le statut du joueur
                        player_found = False
                        for player in self.game_state["players"]:
                            if player["id"] == client_id:
                                player["ready"] = action_data["ready"]
                                player_found = True
                                break
                        
                        # Si le joueur n'est pas dans la liste, l'ajouter
                        if not player_found:
                            # Vérifier que le client est bien connecté
                            client_connected = False
                            for client in self.clients:
                                if client["id"] == client_id:
                                    client_connected = True
                                    break
                            
                            if client_connected:
                                self.game_state["players"].append({
                                    "id": client_id,
                                    "name": f"Joueur {client_id}",
                                    "ready": action_data["ready"]
                                })
                
                # Si le message contient un indicateur de configuration terminée
                if "setup_complete" in action_data:
                    # Mettre à jour le statut du joueur
                    if "players" in self.game_state:
                        for player in self.game_state["players"]:
                            if player["id"] == client_id:
                                player["ready"] = True
                                break
                
                # Mettre à jour le reste de l'état du jeu
                self.game_state.update(action_data)
                print(f"État du jeu mis à jour avec les données du client {client_address}")
            
            # Diffuser la mise à jour à tous les clients
            print("Diffusion de la mise à jour à tous les clients...")
            self.broadcast({
                "type": "game_update",
                "state": self.game_state
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
        """Diffuse un message à tous les clients
        
        Args:
            message: Message à diffuser
        """
        print(f"Diffusion d'un message de type '{message.get('type')}' à tous les clients...")
        
        # Copier la liste des clients pour éviter les problèmes de modification pendant l'itération
        with self.lock:
            clients_copy = self.clients.copy()
        
        # Envoyer le message à chaque client
        for client_info in clients_copy:
            try:
                self.send_to_client(client_info["socket"], message)
            except Exception as e:
                print(f"Erreur lors de la diffusion au client {client_info['address']}: {e}")
                # Ne pas supprimer le client ici, cela sera fait dans le thread de gestion du client
        
        print("Message diffusé à tous les clients")
    
    def send_to_client(self, client_socket, message):
        """Envoie un message à un client
        
        Args:
            client_socket: Socket du client
            message: Message à envoyer
            
        Raises:
            Exception: Si l'envoi échoue
        """
        try:
            # Sérialiser le message
            data = pickle.dumps(message)
            
            # Envoyer la taille des données suivie des données
            client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            client_socket.sendall(data)
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi d'un message: {e}")
            raise
    
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
            "state": self.game_state
        })
        print("Mise à jour diffusée à tous les clients")

    def check_server_accessibility(self):
        """Vérifie si le serveur est accessible depuis l'extérieur"""
        try:
            # Obtenir l'adresse IP externe
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            external_ip = s.getsockname()[0]
            s.close()
            
            print(f"Vérification de l'accessibilité du serveur depuis l'extérieur...")
            print(f"Adresse IP externe: {external_ip}")
            print(f"Port: {self.port}")
            
            # Vérifier si le port est ouvert en essayant de se connecter depuis l'extérieur
            # Note: Cette vérification n'est pas parfaite car elle essaie de se connecter depuis la même machine
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            
            if self.host == '0.0.0.0':
                # Si le serveur écoute sur toutes les interfaces, essayer de se connecter à l'IP externe
                try:
                    test_socket.connect((external_ip, self.port))
                    print(f"Le serveur est accessible depuis l'extérieur sur {external_ip}:{self.port}")
                    test_socket.close()
                except Exception as e:
                    print(f"AVERTISSEMENT: Le serveur pourrait ne pas être accessible depuis l'extérieur: {e}")
                    print("Si vous êtes derrière un routeur, assurez-vous que le port est correctement redirigé.")
                    print("Si vous utilisez un pare-feu, assurez-vous que le port est ouvert.")
            
            print("Pour que d'autres joueurs puissent se connecter, ils doivent utiliser l'adresse IP suivante:")
            print(f"Adresse IP pour les joueurs sur le même réseau local: {external_ip}")
            print("Si les joueurs sont sur un réseau différent, ils devront utiliser votre adresse IP publique.")
            print("Vous pouvez trouver votre adresse IP publique en visitant https://www.whatismyip.com/")
            
        except Exception as e:
            print(f"Erreur lors de la vérification de l'accessibilité du serveur: {e}")

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