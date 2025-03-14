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
            
            # Vérifier si l'adresse IP est valide
            try:
                socket.inet_aton(self.host)
                print(f"Adresse IP valide: {self.host}")
            except socket.error:
                print(f"Adresse IP invalide: {self.host}, tentative de résolution DNS...")
                try:
                    resolved_ip = socket.gethostbyname(self.host)
                    print(f"Résolution DNS réussie: {self.host} -> {resolved_ip}")
                    self.host = resolved_ip
                except socket.gaierror as e:
                    print(f"Erreur de résolution DNS pour {self.host}: {e}")
                    return False
            
            print(f"Connexion à {self.host}:{self.port}...")
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
    
    def reconnect(self):
        """Tente de se reconnecter au serveur
        
        Returns:
            bool: True si la reconnexion a réussi, False sinon
        """
        if self.connected:
            # Vérifier si la connexion est réellement active
            try:
                # Envoyer un message de ping pour vérifier la connexion
                print("Vérification de la connexion existante...")
                self.client_socket.settimeout(2)
                # Envoyer un message vide pour tester la connexion
                self.client_socket.sendall(len(b'ping').to_bytes(4, byteorder='big'))
                self.client_socket.sendall(b'ping')
                self.client_socket.settimeout(None)
                print("Connexion existante fonctionnelle")
                return True
            except Exception as e:
                print(f"La connexion existante ne fonctionne pas: {e}")
                self.connected = False
                # Fermer le socket existant
                try:
                    self.client_socket.close()
                except:
                    pass
        
        print(f"Tentative de reconnexion à {self.host}:{self.port}...")
        
        # Fermer le socket existant s'il existe
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        # Créer un nouveau socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(5)
        
        try:
            print(f"Connexion à {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            self.client_socket.settimeout(None)
            self.connected = True
            
            # Démarrer un nouveau thread de réception si nécessaire
            if not self.receive_thread or not self.receive_thread.is_alive():
                print("Démarrage d'un nouveau thread de réception...")
                self.receive_thread = threading.Thread(target=self.receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            
            print(f"Reconnecté au serveur {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Échec de la reconnexion: {e}")
            return False
    
    def receive_messages(self):
        """Reçoit les messages du serveur"""
        print("Début de la réception des messages...")
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.connected:
            try:
                # Recevoir la taille des données
                print("En attente de données du serveur...")
                # Définir un timeout pour éviter de bloquer indéfiniment
                self.client_socket.settimeout(10)  # 10 secondes de timeout
                size_bytes = self.client_socket.recv(4)
                # Remettre en mode bloquant
                self.client_socket.settimeout(None)
                
                if not size_bytes:
                    print("Aucune donnée reçue du serveur, tentative de reconnexion...")
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"Trop d'erreurs consécutives ({consecutive_errors}), déconnexion")
                        self.connected = False
                        break
                    
                    # Tenter de se reconnecter
                    if self.reconnect():
                        print("Reconnexion réussie, reprise de la réception...")
                        consecutive_errors = 0
                        continue
                    else:
                        # Si la reconnexion échoue, attendre avant de réessayer
                        print("Échec de la reconnexion, attente avant nouvelle tentative...")
                        time.sleep(2)
                        continue
                
                # Réinitialiser le compteur d'erreurs si on reçoit des données
                consecutive_errors = 0
                
                size = int.from_bytes(size_bytes, byteorder='big')
                print(f"Taille des données à recevoir: {size} octets")
                
                # Recevoir les données
                data = b""
                self.client_socket.settimeout(5)  # 5 secondes de timeout pour chaque morceau
                while len(data) < size:
                    chunk = self.client_socket.recv(min(size - len(data), 4096))
                    if not chunk:
                        print("Réception de données interrompue, tentative de reconnexion...")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            print(f"Trop d'erreurs consécutives ({consecutive_errors}), déconnexion")
                            self.connected = False
                            break
                        # Tenter de se reconnecter
                        if self.reconnect():
                            print("Reconnexion réussie, mais données perdues. Attente de nouvelles données...")
                            break
                        # Attendre un peu avant de réessayer
                        time.sleep(2)
                        break
                    data += chunk
                
                # Remettre en mode bloquant
                self.client_socket.settimeout(None)
                
                # Si on a quitté la boucle de réception à cause d'une erreur, continuer la boucle principale
                if len(data) < size:
                    continue
                
                # Réinitialiser le compteur d'erreurs si on reçoit des données complètes
                consecutive_errors = 0
                
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
            # Message de connexion, contient l'ID du client
            client_id = message.get("id")
            print(f"ID client: {client_id}")
            
            # Appeler les callbacks de connexion
            print("Appel des callbacks de connexion...")
            for callback in self.callbacks["connection"]:
                try:
                    callback(client_id)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de connexion: {e}")
        
        elif message_type == "game_start":
            # La partie commence
            print("Signal de démarrage de partie reçu")
            
            # Appeler les callbacks de démarrage de partie
            for callback in self.callbacks["game_start"]:
                try:
                    callback()
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de démarrage de partie: {e}")
        
        elif message_type == "game_update":
            # Mise à jour de l'état du jeu
            game_state = message.get("state", {})
            
            # Stocker l'état du jeu
            self.game_state = game_state
            
            # Appeler les callbacks de mise à jour de l'état du jeu
            for callback in self.callbacks["game_update"]:
                try:
                    callback(game_state)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de mise à jour de l'état du jeu: {e}")
        
        elif message_type == "chat":
            # Message de chat
            sender_id = message.get("sender_id")
            chat_message = message.get("message", "")
            
            # Appeler les callbacks de chat
            for callback in self.callbacks["chat"]:
                try:
                    callback(sender_id, chat_message)
                except Exception as e:
                    print(f"Erreur lors de l'appel du callback de chat: {e}")
                    
        elif message_type == "ack":
            # Accusé de réception du serveur
            ack_message_type = message.get("message_type", "unknown")
            print(f"Accusé de réception pour le message de type '{ack_message_type}'")
            # Pas besoin de faire autre chose, c'est juste pour maintenir la connexion active
        
        else:
            # Type de message inconnu
            print(f"Type de message inconnu: {message_type}")
    
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
            bool: True si le message a été envoyé avec succès, False sinon
        """
        if not self.connected:
            print("Non connecté au serveur, tentative de reconnexion...")
            if not self.reconnect():
                print("Échec de la reconnexion, impossible d'envoyer le message")
                return False
        
        try:
            # Sérialiser le message
            print(f"Sérialisation du message de type '{message.get('type')}'...")
            data = pickle.dumps(message)
            
            # Envoyer la taille des données
            size = len(data)
            print(f"Envoi de {size} octets au serveur...")
            
            try:
                self.client_socket.sendall(size.to_bytes(4, byteorder='big'))
                self.client_socket.sendall(data)
                print("Message envoyé avec succès")
                return True
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"Erreur lors de l'envoi du message: {e}")
                print("Tentative de reconnexion...")
                
                # Tenter de se reconnecter
                if self.reconnect():
                    print("Reconnexion réussie, nouvelle tentative d'envoi...")
                    # Réessayer d'envoyer le message
                    try:
                        self.client_socket.sendall(size.to_bytes(4, byteorder='big'))
                        self.client_socket.sendall(data)
                        print("Message envoyé avec succès après reconnexion")
                        return True
                    except Exception as e2:
                        print(f"Échec de l'envoi après reconnexion: {e2}")
                        self.connected = False
                        return False
                else:
                    print("Échec de la reconnexion")
                    self.connected = False
                    return False
                    
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
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