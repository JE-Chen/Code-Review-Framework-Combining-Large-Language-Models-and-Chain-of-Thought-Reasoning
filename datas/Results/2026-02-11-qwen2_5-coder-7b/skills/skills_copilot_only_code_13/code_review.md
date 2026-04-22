### Summary
This code is a simple Pygame game where the player controls a green rectangle to avoid red rectangles that appear randomly on the screen. The game has a scoring system, and the player's position is constrained within the boundaries of the window.

### Linting Issues
- **Line 9**: Variable names like `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`, and `SPEED` should follow snake_case convention.
- **Line 15**: Unused variable `keys`.
- **Line 16**: Unnecessary use of `global` keyword inside functions.

### Code Smells
- **Long Functions**: Functions like `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop` are quite large, making them harder to understand and test.
- **Magic Numbers**: Values like `30`, `25`, `5`, `640`, `480`, and `36` are hardcoded throughout the code without clear explanations.
- **Global State**: Variables like `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, and `runningGame` are modified globally across multiple functions, leading to potential bugs and maintenance difficulties.