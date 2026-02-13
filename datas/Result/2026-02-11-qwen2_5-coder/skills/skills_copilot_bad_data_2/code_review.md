### Diff #1
#### Summary
This PR introduces several functions and includes some utility code. The primary changes involve adding functions for processing user input, performing conditional logic, and handling global configuration settings. Additionally, it includes a function that uses `eval`, which is generally discouraged due to security risks.

#### Linting Issues
- **File:** example.py  
  - Line 1: Missing docstring for public function `process_user_input`.
  - Line 5: Variable name `hidden_flag` is too generic and could be misleading.
  - Line 19: Function `unsafe_eval` has no docstring and does not handle exceptions properly.
  - Line 30: Global variable `global_config` is accessed directly within the function.

#### Code Smells
- **Function `process_user_input`:**  
  - Performs I/O operations (`print`) within its logic, making it harder to test and reuse.
  - Does not handle different types of invalid input gracefully.
  
- **Function `secret_behavior`:**  
  - Uses a hidden flag, which makes its behavior unpredictable and hard to test.

- **Function `check_value`:**  
  - Returns string literals based on boolean values, which is less readable than using explicit strings.

- **Function `run_task`:**  
  - Uses global state (`global_config`), which can lead to unintended side effects.

- **Function `timestamped_message`:**  
  - Directly calls `time.time()`, making it dependent on the current system time, which is not ideal for testing.

### Diff #2
#### Summary
This diff includes additional utility functions and a modified version of `process_user_input`. The main changes focus on improving code clarity and removing unnecessary I/O operations.

#### Linting Issues
- **File:** example.py  
  - Line 42: Function `f` lacks a docstring.
  - Line 48: Function `multiply` has no docstring.

#### Code Smells
- **Function `process_user_input`:**  
  - Still performs I/O operations, which can complicate testing and reusability.

- **Function `risky_update`:**  
  - Uses exception handling to set a default value, which is fragile and error-prone.

- **Function `timestamped_message`:**  
  - Remains dependent on `time.time()`, which is not suitable for testing environments.

- **Global State Usage:**  
  - Functions like `run_task` still access global state, which can lead to unexpected behavior.