# Jeu des Animaux - Mode en ligne

Ce document explique comment jouer au Jeu des Animaux en ligne avec un ami.

## Prérequis

- Python 3.6 ou supérieur
- Pygame
- Connexion Internet
- Accès au port 5555 (configurable)

## Installation

Assurez-vous que tous les prérequis sont installés :

```bash
pip install pygame
```

## Jouer en ligne

Le jeu utilise une architecture client-serveur. Un joueur doit héberger la partie (serveur) et l'autre joueur doit s'y connecter (client).

### Héberger une partie (Serveur)

1. Lancez le jeu et sélectionnez "Héberger une partie" dans le menu principal
2. Le jeu démarrera automatiquement un serveur sur votre machine (localhost)
3. Configurez votre animal selon vos préférences
4. Attendez qu'un autre joueur se connecte

Alternativement, vous pouvez démarrer le serveur manuellement :

```bash
python server.py
```

Par défaut, le serveur écoute sur l'adresse 127.0.0.1 (localhost) sur le port 5555. Vous pouvez modifier ces paramètres avec les options `--host` et `--port` :

```bash
python server.py --host 0.0.0.0 --port 6000
```

Utiliser `0.0.0.0` comme adresse permet d'accepter des connexions depuis n'importe quelle interface réseau.

### Rejoindre une partie (Client)

1. Lancez le jeu et sélectionnez "Rejoindre une partie" dans le menu principal
2. Entrez l'adresse IP de l'hôte (celle du joueur qui héberge la partie)
3. Configurez votre animal selon vos préférences
4. La partie commencera automatiquement une fois que les deux joueurs auront terminé leur configuration

Alternativement, vous pouvez rejoindre une partie manuellement :

```bash
python main.py
```

Puis sélectionnez "Rejoindre une partie" dans le menu et entrez l'adresse IP de l'hôte.

## Comment jouer

- Chaque joueur contrôle son propre animal, configuré selon ses préférences
- Les joueurs jouent à tour de rôle
- Lorsque c'est votre tour, vous pouvez déplacer votre animal, attaquer l'adversaire, ou boire de l'eau
- Après chaque action, le tour passe automatiquement à l'autre joueur
- Le jeu se termine lorsqu'un des animaux est vaincu

## Améliorations récentes

Le mode multijoueur a été amélioré avec les fonctionnalités suivantes :

1. **Meilleure gestion des connexions** : Le jeu tente plusieurs fois de se connecter au serveur avant d'abandonner.
2. **Gestion robuste des erreurs** : Les erreurs sont capturées et affichées à l'utilisateur.
3. **Récupération après déconnexion** : Le jeu affiche un message clair en cas de déconnexion.
4. **Configuration individuelle des animaux** : Chaque joueur peut configurer son propre animal.
5. **Synchronisation de l'état du jeu** : L'état du jeu est correctement synchronisé entre les joueurs.

## Résolution des problèmes courants

### Le client ne peut pas se connecter au serveur

- Vérifiez que le serveur est bien démarré
- Vérifiez que l'adresse IP est correcte
- Vérifiez que le port est ouvert dans le pare-feu
- Si vous êtes derrière un routeur, assurez-vous que le port est correctement redirigé

### La partie se déconnecte

- Vérifiez votre connexion Internet
- Redémarrez le serveur et les clients
- Essayez d'utiliser un port différent

### Le serveur ne démarre pas

- Vérifiez qu'aucun autre programme n'utilise déjà le port 5555
- Essayez de spécifier un port différent avec l'option `--port`
- Vérifiez les logs pour plus d'informations sur l'erreur

## Remarques techniques

- Le jeu utilise TCP pour la communication réseau
- L'état du jeu est synchronisé après chaque action
- Les messages sont sérialisés avec pickle
- Le serveur peut gérer au maximum 2 joueurs simultanément
- Le mode multijoueur utilise une architecture client-serveur où le serveur fait autorité sur l'état du jeu 