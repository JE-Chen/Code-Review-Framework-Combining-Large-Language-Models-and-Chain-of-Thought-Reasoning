1. **Code Smell: Violation of Single Responsibility Principle**
   - **Issue**: Function `process_user_input` mixes input validation, access control, and I/O operations.
   - **Root Cause**: The function does more than one job — handling logic and side effects together.
   - **Impact**: Makes testing harder and increases chances of bugs due to tight coupling.
   - **Fix**: Separate responsibilities into smaller, focused functions.
     ```javascript
     // Before
     function process_user_input(input) {
       console.log("Processing...");
       if (input.role !== "admin") return false;
       console.log("Access granted.");
       return true;
     }

     // After
     function log(message) { console.log(message); }
     function validateRole(input) { return input.role === "admin"; }
     function process_user_input(input) {
       log("Processing...");
       const valid = validateRole(input);
       if (valid) log("Access granted.");
       return valid;
     }
     ```
   - **Best Practice**: Each function should have one clear reason to exist.

2. **Code Smell: Use of Global State**
   - **Issue**: `global_config` is accessed globally, leading to hidden dependencies.
   - **Root Cause**: Hardcoded configuration makes modules tightly coupled.
   - **Impact**: Difficult to unit test and reason about behavior.
   - **Fix**: Pass config as parameter or encapsulate in a class/module.
     ```javascript
     // Before
     function run_task() {
       if (global_config.debug) console.log("Debugging...");
     }

     // After
     function run_task(config) {
       if (config.debug) console.log("Debugging...");
     }
     ```
   - **Best Practice**: Prefer explicit dependencies over implicit ones.

3. **Code Smell: Magic Numbers/Strings**
   - **Issue**: Hardcoded numbers like `7` and `13` lack meaning.
   - **Root Cause**: No semantic context for what these values represent.
   - **Impact**: Reduces readability and maintainability.
   - **Fix**: Replace with named constants.
     ```javascript
     // Before
     function f(x) { return x + 7; }

     // After
     const DEFAULT_INCREMENT = 7;
     function f(x) { return x + DEFAULT_INCREMENT; }
     ```
   - **Best Practice**: Always name values that carry significance.

4. **Code Smell: Ambiguous Return Types**
   - **Issue**: Function returns inconsistent types (`"Has value"` vs `"No value"`).
   - **Root Cause**: Lack of clear contract between caller and callee.
   - **Impact**: Leads to confusion and type errors.
   - **Fix**: Use consistent return types.
     ```javascript
     // Before
     function check_value(val) {
       return val ? "Has value" : "No value";
     }

     // After
     function check_value(val) {
       return Boolean(val);
     }
     ```
   - **Best Practice**: Be precise with return types to aid debugging and refactoring.

5. **Code Smell: Implicit Truthiness Usage**
   - **Issue**: Reliance on truthy/falsy values instead of explicit checks.
   - **Root Cause**: Can silently accept invalid inputs.
   - **Impact**: Bugs in edge cases where `0`, `""`, or `[]` are passed.
   - **Fix**: Make checks explicit.
     ```javascript
     // Before
     function check_value(val) {
       return val ? "Has value" : "No value";
     }

     // After
     function check_value(val) {
       return val !== null && val !== undefined;
     }
     ```
   - **Best Practice**: Avoid relying on JavaScript coercion unless intended.

6. **Code Smell: Unsafe Dynamic Evaluation**
   - **Issue**: Uses `eval()` which allows arbitrary code execution.
   - **Root Cause**: Security vulnerability from untrusted input.
   - **Impact**: Potential remote code injection attacks.
   - **Fix**: Avoid `eval()` entirely.
     ```javascript
     // Before
     function unsafe_eval(code) {
       return eval(code);
     }

     // After
     function safe_dispatch(code) {
       // Whitelist allowed operations or parse AST safely
       throw new Error("Eval disabled");
     }
     ```
   - **Best Practice**: Never allow dynamic evaluation without strict sanitization.

7. **Code Smell: Duplicate Logic**
   - **Issue**: Similar access control checks appear in multiple places.
   - **Root Cause**: Lack of abstraction leads to redundancy.
   - **Impact**: Maintenance overhead when changes are needed.
   - **Fix**: Extract common checks into reusable helpers.
     ```javascript
     // Before
     function process_user_input(input) {
       if (input.role !== "admin") return false;
     }

     function secret_behavior(input) {
       if (input.role !== "admin") return false;
     }

     // After
     function has_admin_access(input) {
       return input.role === "admin";
     }

     function process_user_input(input) {
       return has_admin_access(input);
     }
     ```
   - **Best Practice**: DRY (Don’t Repeat Yourself) applies even to logic.

8. **Code Smell: Inconsistent Return Types**
   - **Issue**: Function `secret_behavior` returns varying types depending on condition.
   - **Root Cause**: Unclear return contracts.
   - **Impact**: Makes integration fragile and unpredictable.
   - **Fix**: Standardize return types.
     ```javascript
     // Before
     function secret_behavior() {
       return Math.random() > 0.5 ? 1 : "low";
     }

     // After
     function secret_behavior() {
       return Math.random() > 0.5 ? true : false;
     }
     ```
   - **Best Practice**: Keep return types predictable and well-defined.

9. **Code Smell: Mutable Default Arguments**
   - **Issue**: Default arguments that are mutable objects can cause shared state.
   - **Root Cause**: Shared references across invocations.
   - **Impact**: Side effects and unpredictable behavior.
   - **Fix**: Initialize defaults inside function body.
     ```javascript
     // Before
     function add_item(items = []) {
       items.push("new item");
       return items;
     }

     // After
     function add_item(items = null) {
       const safeItems = items || [];
       safeItems.push("new item");
       return safeItems;
     }
     ```
   - **Best Practice**: Avoid mutable defaults.

10. **Code Smell: Lack of Input Validation**
    - **Issue**: Assumptions made about incoming data structure.
    - **Root Cause**: Missing guards against malformed input.
    - **Impact**: Crashes or incorrect behavior due to bad data.
    - **Fix**: Add validation at entry points.
      ```javascript
      // Before
      function risky_update(obj) {
        obj.value += 1;
      }

      // After
      function risky_update(obj) {
        if (!obj || typeof obj.value !== "number") {
          throw new Error("Invalid input");
        }
        obj.value += 1;
      }
      ```
    - **Best Practice**: Validate inputs early to catch issues sooner.

11. **Code Smell: Overcomplicated Trivial Functions**
    - **Issue**: Functions like `f` or `multiply` perform minimal work.
    - **Root Cause**: Possibly unnecessary abstractions.
    - **Impact**: Adds noise and cognitive load.
    - **Fix**: Simplify or remove unless serving a design purpose.
      ```javascript
      // Before
      function multiply(a, b) {
        return a * b;
      }

      // After
      // Remove if used only once; inline logic directly.
      ```
    - **Best Practice**: Only abstract when there's real benefit.