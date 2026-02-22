---

### Code Smell Type: **Global State Abuse**
- **Problem Location:**  
  Global variables like `PLAYER`, `ENEMIES`, `BULLETS`, and `STRANGE_FLAGS` are used throughout the game loop without encapsulation.
- **Detailed Explanation:**  
  Using global mutable state makes code harder to reason about and debug. It increases side effects and reduces modularity. Changes to one part of the code can unexpectedly affect others due to shared mutable state.
- **Improvement Suggestions:**  
  Refactor into classes or structs to encapsulate player, enemies, bullets, and game state. Pass these explicitly where needed instead of relying on globals.
- **Priority Level:** High

---

### Code Smell Type: **Magic Numbers**
- **Problem Location:**  
  The number `17` is hardcoded as `MAGIC`. Also, values like `10`, `15`, `300`, and `60` appear directly in logic.
- **Detailed Explanation:**  
  Magic numbers reduce readability and make future changes error-prone. Without context, readers cannot understand why these specific values were chosen.
- **Improvement Suggestions:**  
  Replace magic numbers with named constants or configuration parameters. For example, `SPAWN_INTERVAL = 17`.
- **Priority Level:** Medium

---

### Code Smell Type: **Long Function**
- **Problem Location:**  
  `do_the_whole_game_because_why_not()` handles rendering, input, physics, collision detection, and game flow — violating the Single Responsibility Principle.
- **Detailed Explanation:**  
  This function does too many things at once, making it hard to test, reuse, or refactor. A long function often indicates poor decomposition.
- **Improvement Suggestions:**  
  Split the function into smaller, focused functions such as `handle_input()`, `update_game_state()`, `render_scene()`, etc.
- **Priority Level:** High

---

### Code Smell Type: **Inefficient List Mutation During Iteration**
- **Problem Location:**  
  Removing items from lists (`BULLETS.remove(b)` and `ENEMIES.remove(e)`) during iteration using slicing (`ENEMIES[:]`) causes performance issues and subtle bugs.
- **Detailed Explanation:**  
  Modifying collections during iteration leads to undefined behavior or skipped elements. This pattern also hurts performance by copying entire lists repeatedly.
- **Improvement Suggestions:**  
  Use list comprehensions or temporary buffers to collect items for removal rather than mutating while iterating.
- **Priority Level:** High

---

### Code Smell Type: **Poor Naming**
- **Problem Location:**  
  Variables like `CLOCK_THING`, `PLAYER`, `ENEMIES`, `BULLETS`, `STRANGE_FLAGS`, and `do_the_whole_game_because_why_not` lack clarity and meaning.
- **Detailed Explanation:**  
  Unclear names obscure intent and make understanding the codebase more difficult. Names should reflect purpose and type clearly.
- **Improvement Suggestions:**  
  Rename `CLOCK_THING` → `clock`, `PLAYER` → `player_state`, `ENEMIES` → `enemy_list`, `BULLETS` → `bullet_list`, `STRANGE_FLAGS` → `game_flags`, `do_the_whole_game_because_why_not` → `run_game_loop`.
- **Priority Level:** Medium

---

### Code Smell Type: **Overuse of Raw Data Structures**
- **Problem Location:**  
  Using dictionaries (`{"x": x, "y": y}`) instead of custom classes or dataclasses for entities.
- **Detailed Explanation:**  
  Dictionaries are flexible but less expressive than typed structures. They increase cognitive load and risk mismatched field usage.
- **Improvement Suggestions:**  
  Define classes like `Player`, `Enemy`, `Bullet` with clear interfaces and methods.
- **Priority Level:** Medium

---

### Code Smell Type: **Lack of Input Validation**
- **Problem Location:**  
  No checks against invalid user inputs or edge cases in movement or collisions.
- **Detailed Explanation:**  
  While not critical here, real-world applications benefit from validating assumptions and preventing crashes or exploits.
- **Improvement Suggestions:**  
  Add bounds checking and defensive programming patterns where appropriate.
- **Priority Level:** Low

---

### Code Smell Type: **Unnecessary Exception Handling**
- **Problem Location:**  
  `try...except` block around bullet/enemy collision logic has no meaningful handling.
- **Detailed Explanation:**  
  Catch-all exceptions mask real errors and prevent proper debugging. In this case, it just swallows any exceptions silently.
- **Improvement Suggestions:**  
  Remove the empty `except:` clause or replace it with targeted error handling or logging.
- **Priority Level:** Medium

---

### Code Smell Type: **Hardcoded Screen Dimensions**
- **Problem Location:**  
  Constants `W = 800`, `H = 600` are hardcoded and reused without abstraction.
- **Detailed Explanation:**  
  Hardcoding screen sizes makes scaling or adapting for different resolutions harder and less maintainable.
- **Improvement Suggestions:**  
  Extract dimensions into a configuration object or class.
- **Priority Level:** Medium

---

### Code Smell Type: **Uncommented Side Effects**
- **Problem Location:**  
  `time.sleep(1)` after quitting and `print(...)` at end are non-standard behaviors.
- **Detailed Explanation:**  
  These actions have side effects outside core gameplay logic and may confuse users or break automated testing.
- **Improvement Suggestions:**  
  Abstract UI lifecycle steps into separate modules or handlers instead of mixing them in main game loop.
- **Priority Level:** Medium

---