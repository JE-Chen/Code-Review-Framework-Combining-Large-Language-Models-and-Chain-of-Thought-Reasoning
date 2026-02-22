### Code Review Summary

#### 1. **Readability & Consistency**
- Indentation and formatting are consistent.
- Comments are minimal; no inline comments or docstrings for functions.
- Suggestion: Add brief docstrings to methods for clarity.

#### 2. **Naming Conventions**
- Global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) are poorly named and violate encapsulation.
- Function names (`handle_btn1`, etc.) are descriptive but could be more specific.
- Suggestion: Use snake_case for Python identifiers and avoid global state.

#### 3. **Software Engineering Standards**
- Heavy use of global variables makes code hard to maintain and test.
- Logic duplication exists in conditional branches inside `handle_btn2`.
- Suggestion: Encapsulate logic into private helper methods and reduce reliance on globals.

#### 4. **Logic & Correctness**
- No explicit error handling for invalid inputs.
- Logic in `handle_btn2` can be simplified for better readability.
- Potential bug: `GLOBAL_MODE` changes without user interaction.

#### 5. **Performance & Security**
- No major performance issues; however, repeated string concatenation may be inefficient.
- No direct security concerns due to limited scope.

#### 6. **Documentation & Testing**
- Missing unit tests for core functionality.
- No inline or external documentation provided.
- Suggestion: Add basic unit tests and improve API documentation.

#### 7. **General Suggestions**
- Replace global variables with instance attributes.
- Modularize conditional logic for clarity.
- Improve naming consistency and add docstrings where needed.

--- 

**Overall Score**: ⚠️ Needs Improvement  
**Key Areas for Improvement**: Global state usage, modularity, and code clarity.