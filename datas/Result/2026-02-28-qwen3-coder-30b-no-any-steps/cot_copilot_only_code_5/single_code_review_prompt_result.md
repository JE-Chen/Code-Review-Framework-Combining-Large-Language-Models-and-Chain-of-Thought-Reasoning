# Code Review: Global State Management

## 1. Linting Issues

- **No syntax errors** detected.
- **Naming convention issues**: 
  - `GLOBAL_STATE` uses all caps but should be `global_state` or `GLOBAL_STATE` with consistent capitalization style.
  - Functions like `init_data`, `increment_counter` use snake_case correctly.
- **Style violations**:
  - Missing docstrings on functions.
  - No type hints provided.
- **Formatting inconsistencies**:
  - Indentation appears correct.
- **Language-specific best practices**:
  - Using global mutable state instead of encapsulation.

## 2. Code Smells

- **God object pattern**: `GLOBAL_STATE` holds multiple unrelated data types.
- **Primitive obsession**: Using primitive values without structure.
- **Magic numbers**: `77` hardcoded as threshold value.
- **Tight coupling**: Direct dependency on `GLOBAL_STATE`.
- **Feature envy**: Functions directly access `GLOBAL_STATE` rather than receiving dependencies.
- **Poor separation of concerns**: Mixing business logic with state management.
- **Overly complex conditionals**: Nested conditional logic in `process_items`.

## 3. Maintainability

- **Readability**: Low due to tight coupling and global access.
- **Modularity**: Poor - functions depend on shared state.
- **Reusability**: Minimal - tightly coupled to specific global state.
- **Testability**: Difficult due to reliance on global mutable state.
- **SOLID violations**:
  - Single Responsibility Principle violated by `GLOBAL_STATE`.
  - Dependency Inversion Principle not followed.

## 4. Performance Concerns

- **Inefficient loops**: Loop over list elements in `process_items` has O(n) time complexity which is acceptable.
- **Unnecessary computations**: None detected beyond required processing.
- **Memory issues**: No significant memory leaks expected.
- **Blocking operations**: Not blocking; synchronous processing.
- **Algorithmic complexity**: O(n) linear processing for `process_items`.

## 5. Security Risks

- **None detected** for current implementation scope.
- No user inputs or external system interactions present.

## 6. Edge Cases & Bugs

- **Null/undefined handling**: Not applicable since no optional fields.
- **Boundary conditions**: No special case handling for edge values.
- **Race conditions**: Not possible in single-threaded execution context.
- **Unhandled exceptions**: No explicit error handling mechanisms.

## 7. Suggested Improvements

### Refactor Global State Usage

#### Before:
```python
GLOBAL_STATE = {
    "counter": 0,
    "data": [],
    "mode": "default",
    "threshold": 77,
    "flag": False
}
```

#### After:
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AppState:
    counter: int = 0
    data: List[int] = None
    mode: str = "default"
    threshold: int = 77
    flag: bool = False
    
    def __post_init__(self):
        if self.data is None:
            self.data = []

app_state = AppState()
```

### Improve Function Encapsulation

#### Before:
```python
def init_data():
    GLOBAL_STATE["data"] = [i for i in range(1, 21)]
    GLOBAL_STATE["counter"] = len(GLOBAL_STATE["data"])
```

#### After:
```python
def init_data(state: AppState):
    state.data = list(range(1, 21))
    state.counter = len(state.data)
```

### Reduce Complexity in Process Items

#### Before:
```python
def process_items():
    results = []
    for item in GLOBAL_STATE["data"]:
        if GLOBAL_STATE["flag"]:
            if item % 2 == 0:
                results.append(item * 2)
            else:
                results.append(item * 3)
        else:
            if item > GLOBAL_STATE["threshold"]:
                results.append(item - GLOBAL_STATE["threshold"])
            else:
                results.append(item + GLOBAL_STATE["threshold"])
    return results
```

#### After:
```python
def process_items(state: AppState) -> List[int]:
    def transform_item(item: int) -> int:
        if state.flag:
            return item * 2 if item % 2 == 0 else item * 3
        else:
            return item - state.threshold if item > state.threshold else item + state.threshold
    
    return [transform_item(item) for item in state.data]
```

### Add Type Hints and Documentation

```python
def increment_counter(state: AppState) -> int:
    """Increment and return updated counter."""
    state.counter += 1
    return state.counter

def toggle_flag(state: AppState) -> bool:
    """Toggle flag and return new value."""
    state.flag = not state.flag
    return state.flag
```

### Key Improvements Summary:
1. Replace global mutable state with encapsulated object.
2. Eliminate magic numbers via configurable parameters.
3. Simplify control flow logic.
4. Add type hints and documentation.
5. Enable easier testing through dependency injection.
6. Follow SOLID principles by separating concerns.

These changes will improve maintainability, testability, and reduce coupling between components.