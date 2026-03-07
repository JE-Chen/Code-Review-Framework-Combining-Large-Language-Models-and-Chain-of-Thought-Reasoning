- **Global Variables & State Management**:  
  Overuse of global variables (`playerX`, `enemyList`, `scoreValue`, etc.) creates tight coupling and complicates testing. Replace with encapsulated state (e.g., `Player` class, `Enemy` objects) for better modularity.

- **Enemy Representation**:  
  `enemyList` stores enemies as `[x, y]` lists. Use tuples or dedicated `Enemy` objects (e.g., `enemy = (x, y)`) for clearer semantics and safer mutation.

- **Boundary Checks**:  
  Player boundary logic is duplicated across four `if` statements. Consolidate into a single helper function (e.g., `clamp_position(x, min, max)`) to reduce redundancy.

- **Collision Handling**:  
  When an enemy is hit, its position is reset *during* iteration. This is acceptable for the current scope but risks unintended behavior if enemy data structures change. Consider safer patterns (e.g., marking enemies for reset after iteration).

- **Naming Clarity**:  
  `vx`/`vy` are acceptable for velocity, but `enemyList` should be more descriptive (e.g., `enemies`). Avoid single-letter variables like `e` in loops—use `enemy` instead.

- **Documentation**:  
  Missing function docstrings and inline comments. Add brief explanations for key logic (e.g., collision detection, boundary rules).

- **Testing Barrier**:  
  Global state prevents unit testing. Refactor to inject dependencies (e.g., pass `screen` to `drawEverything()`) for testability.

- **Minor Formatting**:  
  Align `if`/`elif` conditions consistently (e.g., `playerX < 0` → `playerX = 0`). Add whitespace around operators for readability (e.g., `playerX + PLAYER_SIZE > e[0]`).