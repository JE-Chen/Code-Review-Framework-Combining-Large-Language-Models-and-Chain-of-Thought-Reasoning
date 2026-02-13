- **Naming Conventions**:  
  Rename `enemyList` → `enemies` (plural form for collection) and `scoreValue` → `score` for semantic clarity.  
  Use `_` instead of `i` in `initGame`'s loop (`for _ in range(9)`).

- **Readability & Consistency**:  
  Add docstrings to functions (e.g., `def initGame():` → `"""Initialize Pygame and game state."""`).  
  Replace global variables with a `Game` class for encapsulation (e.g., `player_x`, `enemies` as instance attributes).

- **Logic & Correctness**:  
  In `checkCollision`, the collision condition is correct but overly verbose. Simplify to:  
  ```python
  if (playerX < e[0] + ENEMY_SIZE and 
      playerX + PLAYER_SIZE > e[0] and 
      playerY < e[1] + ENEMY_SIZE and 
      playerY + PLAYER_SIZE > e[1]):
  ```
  (Note: The existing condition is valid but adding line breaks improves readability.)

- **Documentation**:  
  Add comments explaining boundary checks in `movePlayer` (e.g., `# Clamp player within screen bounds`).

- **Software Engineering**:  
  Avoid global state—encapsulate `playerX`, `playerY`, `enemyList`, and `scoreValue` in a class to improve testability and reduce side effects.  
  *Example*: Replace `enemyList` with a class attribute holding enemy positions.