Title: Simple Pygame Game Implementation

Overview: This Python script creates a basic game using the Pygame library where a green square (player) moves around the screen, avoiding red squares (enemies). The player's score increases when they collide with an enemy, which resets the enemy's position to a new random location.

Detailed Explanation:

- **Imports**: The script imports necessary modules like `pygame`, `random`, and `sys`.
  
- **Global Variables**:
  - `screen`: The main display surface.
  - `playerX`, `playerY`: Player's coordinates.
  - `vx`, `vy`: Velocity of the player.
  - `enemyList`: List of enemy positions.
  - `scoreValue`: Current score.
  - `runningGame`: Boolean to control the game loop.
  
- **Constants**:
  - Screen dimensions (`WIDTH`, `HEIGHT`).
  - Player and enemy sizes (`PLAYER_SIZE`, `ENEMY_SIZE`).
  - Movement speed (`SPEED`).

- **Functions**:
  - `initGame()`: Initializes Pygame, sets up the window, and places enemies randomly on the screen.
  - `movePlayer(keys)`: Updates player position based on key presses, ensuring it stays within bounds.
  - `drawEverything()`: Clears the screen, draws the player and enemies, and displays the score.
  - `checkCollision()`: Checks for collisions between the player and enemies, updating scores and resetting enemy positions.
  - `mainLoop()`: Main game loop that handles events, updates game state, and renders the frame at 27 FPS.
  - `endGame()`: Quits Pygame and exits the program.

- **Main Execution**: Calls initialization, starts the main loop, and ends the game upon exit.

Improvements:
1. **Boundary Collision Handling**: Simplify boundary collision logic in `movePlayer`.
2. **Enemy Spawning**: Add functionality to spawn enemies over time instead of all at once.
3. **Score Tracking**: Implement proper scoring system with high score tracking.
4. **Graphics**: Use images for player and enemies instead of rectangles.
5. **Sound Effects**: Add sound effects for collisions and other game actions.
6. **High Score Storage**: Store and retrieve high scores from a file or database.

Example Usage:
To run this game, ensure Pygame is installed (`pip install pygame`). Save the script as `game.py` and execute it with Python:
```sh
python game.py
```
This will open a window displaying the game, allowing you to play by moving the green square with arrow keys.