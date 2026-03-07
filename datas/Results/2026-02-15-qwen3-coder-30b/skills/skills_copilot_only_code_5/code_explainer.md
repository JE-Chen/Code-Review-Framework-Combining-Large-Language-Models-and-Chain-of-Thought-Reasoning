# Global State Manager with Data Processing

## Overview
This code implements a simple global state management system with data processing capabilities. It maintains shared state variables and provides functions to manipulate that state and process data based on current conditions.

## Detailed Explanation

**Global State Structure:**
- `counter`: Tracks processed items count
- `data`: List of integers from 1-20
- `mode`: Current operational mode ("default" or "reset")
- `threshold`: Numeric boundary for conditional logic
- `flag`: Boolean control for processing rules

**Step-by-Step Flow:**

1. **Initialization**: `init_data()` populates data array and sets counter to 20
2. **State Toggle**: `toggle_flag()` switches boolean flag from False to True
3. **Data Processing**: `process_items()` applies different math operations based on flag value:
   - When flag=True: Even numbers doubled, odd numbers tripled
   - When flag=False: Values above threshold subtracted by threshold, others added to threshold
4. **Counter Update**: `increment_counter()` increases counter by 1
5. **State Reset**: `reset_state()` clears all data and resets mode

**Key Functions:**
- `init_data()`: Sets up initial dataset
- `increment_counter()`: Updates counter state
- `toggle_flag()`: Flips boolean control flag
- `process_items()`: Core business logic with conditional branching
- `reset_state()`: Resets entire global state

## Improvements
- Replace global variables with proper class encapsulation
- Add input validation and error handling
- Implement thread safety for concurrent access
- Add logging instead of direct console output
- Separate configuration from business logic

## Example Usage
```
Initial counter: 20
Flag status: True
Processed results: [3, 4, 9, 8, 15, 12, 21, 16, 27, 20, 33, 24, 39, 28, 45, 32, 51, 36, 57, 40]
Counter after increment: 21
State after reset: {'counter': 0, 'data': [], 'mode': 'reset', 'threshold': 77, 'flag': False}
```