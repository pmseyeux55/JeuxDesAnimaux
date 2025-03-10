# Corrections du Mode Multijoueur

Ce document résume les modifications apportées pour résoudre les problèmes du mode multijoueur dans le Jeu des Animaux.

## Problèmes identifiés

1. **Problème de connexion au serveur** : Le client ne parvenait pas à se connecter au serveur local.
2. **Gestion des erreurs insuffisante** : Les erreurs n'étaient pas correctement capturées et affichées.
3. **Problème de déconnexion** : Le jeu ne gérait pas correctement les déconnexions.
4. **Problème d'initialisation de la police** : Erreur "font not initialized" lors de la déconnexion.
5. **Problème de synchronisation** : L'état du jeu n'était pas correctement synchronisé entre les joueurs.

## Solutions implémentées

### 1. Amélioration du serveur (`server.py`)

- Changement de l'adresse d'écoute par défaut de `0.0.0.0` à `127.0.0.1` pour éviter les problèmes de pare-feu.
- Ajout d'une vérification de disponibilité du port avant de démarrer le serveur.
- Utilisation de `time.sleep()` au lieu de `input()` pour éviter de bloquer le serveur.
- Amélioration de la gestion des erreurs avec des messages plus détaillés.

### 2. Amélioration du client réseau (`network/client.py`)

- Ajout d'un timeout pour la connexion au serveur.
- Gestion spécifique des erreurs de connexion (timeout, connexion refusée).
- Amélioration des messages de débogage pour faciliter l'identification des problèmes.

### 3. Amélioration de l'interface réseau (`client.py`)

- Ajout d'un indicateur de connexion perdue (`connection_error`).
- Amélioration de la gestion des erreurs dans les callbacks.
- Correction du problème d'initialisation de la police lors de l'affichage du message de déconnexion.
- Ajout d'une boucle d'attente après déconnexion pour permettre à l'utilisateur de quitter proprement.

### 4. Amélioration de la sérialisation de l'état du jeu (`network/game_state.py`)

- Ajout de gestion d'erreurs dans les méthodes `encode_game_state` et `decode_game_state`.
- Vérification du type des données reçues pour éviter les erreurs de désérialisation.
- Retour d'un état minimal en cas d'erreur d'encodage.

### 5. Amélioration du programme principal (`main.py`)

- Ajout d'une fonction de nettoyage (`cleanup`) pour arrêter proprement le serveur.
- Utilisation du chemin absolu pour le script du serveur.
- Vérification de la disponibilité du port avant de démarrer le serveur.
- Tentatives multiples de connexion au serveur.
- Amélioration de la gestion des erreurs avec des messages plus détaillés.

## Comment tester les modifications

1. Lancez le jeu avec `python main.py`.
2. Sélectionnez "Héberger une partie" dans le menu principal.
3. Configurez votre animal selon vos préférences.
4. Dans une autre fenêtre, lancez une autre instance du jeu et sélectionnez "Rejoindre une partie".
5. Entrez `127.0.0.1` comme adresse IP de l'hôte.
6. Configurez votre animal selon vos préférences.
7. La partie devrait commencer automatiquement une fois que les deux joueurs ont terminé leur configuration.

## Remarques techniques

- Le mode multijoueur utilise une architecture client-serveur où le serveur fait autorité sur l'état du jeu.
- Les messages sont sérialisés avec pickle pour la transmission sur le réseau.
- Le serveur peut gérer au maximum 2 joueurs simultanément.
- La synchronisation de l'état du jeu se fait après chaque action d'un joueur.
- Les erreurs sont capturées et affichées à l'utilisateur pour faciliter le débogage. 