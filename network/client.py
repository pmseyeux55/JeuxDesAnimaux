"""
Module client pour le jeu des animaux.
Gère la connexion au serveur et la synchronisation du jeu.
"""
import socket
import threading
import pickle
import time
import traceback

class GameClient:
    """Client de jeu pour le jeu des animaux"""
    
    def __init__(self, host='localhost', port=5555):
        """Initialise le client
        
        Args:
            host: Adresse IP du serveur
            port: Port du serveur
        """
        print(f"Initialisation du client pour se connecter à {host}:{port}")
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.client_id = None
        self.game_state = {}
        self.callbacks = {
            "connection": [],
            "game_start": [],
            "game_update": [],
            "chat": [],
            "disconnect": []
        }
        self.receive_thread = None
    
    def connect(self):
        """Se connecte au serveur
        
        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        try:
            print(f"Tentative de connexion à {self.host}:{self.port}...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Définir un timeout pour la connexion
            self.client_socket.settimeout(5)
            self.client_socket.connect((self.host, self.port))
            # Remettre le socket en mode bloquant après la connexion
            self.client_socket.settimeout(None)
            self.connected = True
            
            # Démarrer le thread de réception
            print("Démarrage du thread de réception...")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Connecté au serveur {self.host}:{self.port}")
            return True
        except socket.timeout:
            print(f"Timeout lors de la connexion au serveur {self.host}:{self.port}")
            return False
        except ConnectionRefusedError:
            print(f"Connexion refusée par le serveur {self.host}:{self.port}")
            return False
        except Exception as e:
            print(f"Erreur lors de la connexion au serveur: {e}")
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """Se déconnecte du serveur"""
        print("Déconnexion du serveur...")
        self.connected = False
        
        if self.client_socket:
            try:
                print("Fermeture du socket client...")
                self.client_socket.close()
                print("Socket client fermé")
            except Exception as e:
                print(f"Erreur lors de la fermeture du socket client: {e}")
            
        print("Déconnecté du serveur")
        
        # Appeler les callbacks de déconnexion
        print("Appel des callbacks de déconnexion...")
        for callback in self.callbacks["disconnect"]:
            try:
                callback()
            except Exception as e:
                print(f"Erreur lors de l'appel du callback de déconnexion: {e}")
    
    def receive_messages(self):
        """Reçoit les messages du serveur"""
        print("Début de la réception des messages...")
        while self.connected:
            try:
                # Recevoir la taille des données
                print("En attente de données du serveur...")
                size_bytes = self.client_socket.recv(4)
                if not size_bytes:
                    print("Aucune donnée reçue du serveur, déconnexion")
                    break
                
                size = int.from_bytes(size_bytes, byteorder='big')
                print(f"Taille des données à recevoir: {size} octets")
                
                # Recevoir les données
                data = b""
                while len(data) < size:
                    chunk = self.client_socket.recv(min(size - len(data), 4096))
                    if not chunk:
                        print("Réception de données interrompue, déconnexion")
                        break
                    data += chunk
                
                if not data:
                    print("Aucune donnée reçue, déconnexion")
                    break
                
                # Désérialiser les données
                print("Désérialisation des données reçues...")
                message = pickle.loads(data)
                print(f"Message reçu du serveur: {message.get('type', 'inconnu')}")
                
                # Traiter le message
                self.process_message(message)
                
            except Exception as e:
                print(f"Erreur lors de la réception d'un message: {e}")
                traceback.print_exc()
                break
        
        # Si on sort de la boucle, c'est qu'on est déconnecté
        print("Fin de la réception des messages")
        if self.connected:
            print("Déconnexion suite à une erreur de réception")
            self.disconnect()
    
    def process_message(self, message):
        """Traite un message reçu du serveur
        
        Args:
            message: Message reçu
        """
        message_type = message.get("type")
        print(f"Traitement du message de type '{message_type}'")
        
        if message_type == "connection":
            # Connexion établie, récupérer l'ID du client
            self.client_id = message.get("id")
            print(f"ID client: {self.client_id}")
            
            # Appeler les callbacks de connexion
            print("Appel des callbacks de connexion...")
            for callback in self.callbacks["connection"]:
                try:
                    callback(self.client_id)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de connexion: {e}")
        
        elif message_type == "game_start":
            # La partie commence
            print("La partie commence")
            
            # Appeler les callbacks de début de partie
            print("Appel des callbacks de début de partie...")
            for callback in self.callbacks["game_start"]:
                try:
                    callback()
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de début de partie: {e}")
        
        elif message_type == "game_update":
            # Mise à jour de l'état du jeu
            print("Mise à jour de l'état du jeu reçue")
            self.game_state = message.get("state", {})
            
            # Appeler les callbacks de mise à jour du jeu
            print("Appel des callbacks de mise à jour du jeu...")
            for callback in self.callbacks["game_update"]:
                try:
                    callback(self.game_state)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de mise à jour du jeu: {e}")
        
        elif message_type == "chat":
            # Message de chat reçu
            sender_id = message.get("sender_id")
            chat_message = message.get("message", "")
            print(f"Message de chat reçu du joueur {sender_id}: {chat_message}")
            
            # Appeler les callbacks de chat
            print("Appel des callbacks de chat...")
            for callback in self.callbacks["chat"]:
                try:
                    callback(sender_id, chat_message)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de chat: {e}")
    
    def send_action(self, action_data):
        """Envoie une action au serveur
        
        Args:
            action_data: Données de l'action
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        print("Envoi d'une action au serveur...")
        message = {
            "type": "action",
            "data": action_data
        }
        success = self.send_message(message)
        if success:
            print("Action envoyée avec succès")
        else:
            print("Échec de l'envoi de l'action")
        return success
    
    def send_chat(self, message_text):
        """Envoie un message de chat au serveur
        
        Args:
            message_text: Texte du message
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        print(f"Envoi d'un message de chat: {message_text}")
        message = {
            "type": "chat",
            "message": message_text
        }
        success = self.send_message(message)
        if success:
            print("Message de chat envoyé avec succès")
        else:
            print("Échec de l'envoi du message de chat")
        return success
    
    def send_message(self, message):
        """Envoie un message au serveur
        
        Args:
            message: Message à envoyer
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        if not self.connected:
            print("Non connecté au serveur")
            return False
        
        try:
            # Sérialiser le message
            print(f"Sérialisation du message de type '{message.get('type')}'...")
            data = pickle.dumps(message)
            
            # Envoyer la taille des données suivie des données
            print(f"Envoi de {len(data)} octets au serveur...")
            self.client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            self.client_socket.sendall(data)
            print("Message envoyé avec succès")
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi d'un message: {e}")
            traceback.print_exc()
            return False
    
    def register_callback(self, event_type, callback):
        """Enregistre une fonction de rappel pour un type d'événement
        
        Args:
            event_type: Type d'événement ("connection", "game_start", "game_update", "chat", "disconnect")
            callback: Fonction à appeler lorsque l'événement se produit
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        if event_type not in self.callbacks:
            print(f"Type d'événement inconnu: {event_type}")
            return False
        
        print(f"Enregistrement d'un callback pour l'événement '{event_type}'")
        self.callbacks[event_type].append(callback)
        return True
    
    def unregister_callback(self, event_type, callback):
        """Supprime une fonction de rappel pour un type d'événement
        
        Args:
            event_type: Type d'événement
            callback: Fonction à supprimer
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        if event_type not in self.callbacks:
            print(f"Type d'événement inconnu: {event_type}")
            return False
        
        print(f"Suppression d'un callback pour l'événement '{event_type}'")
        if callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            print("Callback supprimé avec succès")
            return True
        
        print("Callback non trouvé")
        return False

# Fonction pour se connecter à un serveur en mode autonome
def connect_to_server(host='localhost', port=5555):
    """Se connecte à un serveur de jeu
    
    Args:
        host: Adresse IP du serveur
        port: Port du serveur
        
    Returns:
        GameClient: Instance du client
    """
    client = GameClient(host, port)
    if client.connect():
        return client
    return None

if __name__ == "__main__":
    # Se connecter au serveur en mode autonome
    client = connect_to_server()
    
    if client:
        try:
            # Garder le client en cours d'exécution
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Se déconnecter proprement
            client.disconnect() 