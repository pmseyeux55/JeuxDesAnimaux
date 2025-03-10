# Jeux Des Animaux (Animal Games)

A strategic turn-based game where animals battle using their unique attributes and abilities.

## Features

- **Single Player Mode**: Play against the computer
- **Multiplayer Mode**: Play with a friend over a network
- **Customizable Animals**: Configure your animal's attributes (health, stamina, speed, teeth, claws, skin, height)
- **Strategic Gameplay**: Use different actions (walk, run, bite, slap) to defeat your opponent
- **Resource Management**: Manage your animal's stamina, hunger, and thirst

## Requirements

- Python 3.6 or higher
- Pygame

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/JeuxDesAnimaux.git
cd JeuxDesAnimaux
```

2. Install the required dependencies:
```bash
pip install pygame
```

## How to Play

### Single Player Mode

Run the game and select "Single Player" from the main menu:
```bash
python main.py
```

### Multiplayer Mode

#### Host a Game
1. Run the game and select "Host Game" from the main menu
2. Configure your animal
3. Wait for another player to join

#### Join a Game
1. Run the game and select "Join Game" from the main menu
2. Enter the host's IP address
3. Configure your animal

For more detailed instructions on multiplayer mode, see [README_ONLINE.md](README_ONLINE.md).

## Game Controls

- **Mouse**: Click to select actions and move your animal
- **Shift + Click**: Special actions (depends on context)

## Recent Improvements

- Enhanced multiplayer connectivity
- Improved error handling
- Better disconnection recovery
- Individual animal configuration for each player
- Improved game state synchronization

For details on recent fixes to the multiplayer mode, see [MULTIPLAYER_FIXES.md](MULTIPLAYER_FIXES.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped improve this game
- Special thanks to the Pygame community for their excellent library 