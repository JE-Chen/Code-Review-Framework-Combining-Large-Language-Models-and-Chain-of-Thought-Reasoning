- **Global State Anti-Pattern**: Avoid module-level globals like `GLOBAL_DATA_THING` and `GLOBAL_FLAG`. These create hidden dependencies, make testing impossible, and risk inconsistent state. Replace with instance attributes (e.g., `self.data_frame`, `self.is_dirty`).
- **Poor Naming**: Rename ambiguous methods:  
  `make_data_somehow` → `generate_data`,  
  `analyze_in_a_hurry` → `analyze_data`,  
  `weird_counter` → `analysis_count`.  
  *Reason: "weird" is subjective; "count" accurately describes purpose.*
- **UI Blocking**: Remove `time.sleep(0.05)` in event handlers. This freezes the UI. Use non-blocking operations (e.g., move data generation to a background thread).
- **Buggy Error Handling**:  
  - `make_data_somehow` fails silently if DataFrame creation fails (crashes later when accessing `len(GLOBAL_DATA_THING)`).  
  - Broad `except` clauses in `analyze_in_a_hurry` swallow all errors.  
  *Fix: Handle specific exceptions and provide user feedback (e.g., `self.info.setText("Error: Failed to generate data")`)*.
- **Magic Number**: Replace `MAGIC_NUMBER = 42` with a named constant like `MAGIC_MULTIPLIER = 42` and add a docstring explaining its purpose.
- **Inefficient Logic**: Using `.iloc[i]` in loops (e.g., `analyze_in_a_hurry`) is slow. Prefer vectorized operations (e.g., `df["mix"] = ...`).
- **Redundant Checks**: `GLOBAL_FLAG["dirty"]` is unnecessary—use `self.is_dirty` instead. Global state complicates tracking.