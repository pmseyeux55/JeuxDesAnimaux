# Guide de Configuration du Mode Multijoueur

Ce guide vous aidera, vous et votre ami, à configurer et jouer au Jeu des Animaux en mode multijoueur.

## Prérequis

- Chaque joueur doit avoir une copie du jeu
- Les deux joueurs doivent être connectés au même réseau (ou avoir une connexion Internet)
- Python 3.6+ et Pygame installés sur les deux ordinateurs

## Configuration

### Pour l'hôte (celui qui héberge la partie)

1. Lancez le jeu avec `python main.py`
2. Sélectionnez "Mode Multijoueur" dans le menu principal
3. Notez votre adresse IP affichée en haut de l'écran (par exemple: "Votre IP: 192.168.1.5")
4. Partagez cette adresse IP avec votre ami (par message, email, etc.)
5. Cliquez sur "Héberger une partie"
6. Configurez votre animal selon vos préférences
7. Attendez que votre ami se connecte

### Pour le client (celui qui rejoint la partie)

1. Lancez le jeu avec `python main.py`
2. Sélectionnez "Mode Multijoueur" dans le menu principal
3. Entrez l'adresse IP de l'hôte dans le champ de saisie
4. Cliquez sur "Rejoindre une partie"
5. Configurez votre animal selon vos préférences
6. La partie commencera automatiquement une fois que les deux joueurs auront terminé leur configuration

## Résolution des problèmes

### L'adresse IP n'est pas affichée

Si l'adresse IP n'est pas affichée dans le menu multijoueur, cela peut être dû à:
- Une déconnexion du réseau
- Un problème avec la détection de l'adresse IP

Solution: Utilisez la commande `ipconfig` (Windows) ou `ifconfig` (macOS/Linux) dans un terminal pour trouver votre adresse IP manuellement.

### Impossible de se connecter

Si le client ne peut pas se connecter à l'hôte, vérifiez:
1. Que les deux ordinateurs sont sur le même réseau
2. Que l'adresse IP est correctement saisie
3. Que le pare-feu n'est pas en train de bloquer la connexion
4. Que le port 5555 est ouvert

### La partie se déconnecte

Si la partie se déconnecte pendant le jeu:
1. Vérifiez votre connexion réseau
2. Redémarrez le jeu sur les deux ordinateurs
3. Essayez de vous reconnecter

## Conseils pour jouer en multijoueur

- Chaque joueur contrôle son propre animal
- Les joueurs jouent à tour de rôle
- Utilisez les différentes actions (marcher, courir, mordre, gifler) stratégiquement
- Gérez bien vos ressources (stamina, faim, soif)
- Communiquez avec votre ami pour une meilleure expérience de jeu

Amusez-vous bien! 