## Code Review: bad_requests.py

### ⚠️ **Critical Issues**

**1. Global State Dependencies**
- *Issue*: Uses global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) making functions non-deterministic
- *Impact*: Hard to test, debug, and reason about behavior
- *Fix*: Pass dependencies as parameters or use dependency injection

**2. Bare Exception Handling**
- *Issue*: `except:` catches all exceptions without logging or proper handling
- *Impact*: Silent failures that mask real problems
- *Fix*: Catch specific exceptions or at minimum log them properly

### 🛠️ **Major Improvements Needed**

**3. Function Responsibilities**
- *Issue*: Single function does multiple unrelated operations
- *Impact*: Violates single responsibility principle
- *Fix*: Split into smaller, focused functions

**4. Variable Naming**
- *Issue*: Poor naming (`weirdVariableName`, `r2`)
- *Impact*: Reduces code readability and maintainability
- *Fix*: Use descriptive, meaningful names

### ✅ **Minor Issues**

**5. Hardcoded Values**
- *Issue*: URLs and data hardcoded throughout
- *Impact*: Difficult to configure and test
- *Fix*: Externalize configuration

**6. Inconsistent Logging**
- *Issue*: Mixed languages (中文/英文) in output
- *Impact*: Poor user experience
- *Fix*: Standardize output format

### 💡 **Recommendations**

1. **Refactor**: Break down monolithic function into smaller units
2. **Improve Error Handling**: Add proper exception logging and handling
3. **Use Configuration**: Externalize hard-coded values
4. **Follow Conventions**: Use Python naming conventions and standards

### 📝 **Overall Assessment**
This code demonstrates several anti-patterns common in quick prototypes. While functional, it requires significant refactoring for production use. Focus on separating concerns, improving error handling, and eliminating global state dependencies.