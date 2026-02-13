### PR Summary

- **Key changes**: Implemented a basic game loop with player movement, score tracking, and dynamic color cycling.  
- **Impact scope**: Entire game logic in new `game.py` (single-file implementation).  
- **Purpose of changes**: To provide a minimal demonstration framework for event handling and state management.  
- **Risks and considerations**:  
  - Global state (`STATE`) creates tight coupling and potential bugs (e.g., negative velocity causes unintended movement direction).  
  - `do_everything()` mixes unrelated logic (score, color, velocity), reducing maintainability.  
  - Movement logic uses redundant operations (e.g., `math.sqrt` for velocity) and lacks clarity.  
- **Items to confirm**:  
  - Verify player movement directionality when velocity is negative.  
  - Refactor global state into a class for better encapsulation and testability.  
  - Simplify score calculation to avoid modulo confusion.