
    Your task is to look at a given git diff that
    represents a Python code change, linter
    feedback and code smells detected in the code
    change, and a corresponding review comment
    about the diff. You need to rate how concise,
    comprehensive, and relevant a review is and
    whether it touches upon all the important
    topics, code smells, vulnerabilities, and
    issues in the code change.
    
    Code Change:
    


    
    
    Code Smells:
    Here is the professional code review conducted according to the provided global rules and requirements.

---

### 1. Code Smell: Violation of Single Responsibility Principle (SRP) & Tight Coupling
- **Problem Location**: `ExportManager.create_exporter()`
- **Detailed Explanation**: The `ExportManager` is responsible for both managing the export lifecycle and the logic for instantiating specific exporters. This creates tight coupling between the manager and every concrete exporter implementation. If a new exporter type is added, `ExportManager` must be modified, violating the Open/Closed Principle.
- **Improvement Suggestions**: Implement a **Factory Pattern** or a Registry. Move the creation logic to a dedicated `ExporterFactory` class or use a dictionary mapping to resolve exporter classes.
- **Priority Level**: High

---

### 2. Code Smell: Refused Bequest (Interface Pollution)
- **Problem Location**: `BaseExporter.finish()` and its implementation in subclasses.
- **Detailed Explanation**: The `BaseExporter` defines a `finish()` method that `JsonLikeExporter` ignores and `ReportService` never calls. When a subclass inherits methods it doesn't need, it indicates a flawed abstraction.
- **Improvement Suggestions**: Remove `finish()` from the base class. If only some exporters need a cleanup phase, create a separate interface (e.g., `DisposableExporter`) or handle the lifecycle differently in the service layer.
- **Priority Level**: Medium

---

### 3. Code Smell: Redundant/Inefficient Logic (Performance Bottleneck)
- **Problem Location**: `ReportService.generate()` inside the `for ch in prepared` loop.
- **Detailed Explanation**: 
  ```python
  buffer = ""
  for ch in prepared:
      buffer = buffer + ch
  ```
  This loop manually reconstructs a string character by character. In Python, strings are immutable, meaning every concatenation creates a new string object. This results in $O(n^2)$ time complexity. Furthermore, it serves no logical purpose as `prepared` is already a string.
- **Improvement Suggestions**: Remove the loop entirely and pass `prepared` directly to `self.exporter.export()`.
- **Priority Level**: High

---

### 4. Code Smell: Hard-coded Dependency & Global State Reliance
- **Problem Location**: `ReportFormatter.format()` and `ExportManager.create_exporter()` accessing `CONFIG`.
- **Detailed Explanation**: The classes rely on a global `CONFIG` dictionary. This makes the code difficult to test in parallel (global state interference) and hides dependencies. A developer looking at the `ReportFormatter` constructor doesn't know it depends on external configuration.
- **Improvement Suggestions**: Use **Dependency Injection**. Pass the necessary configuration values (e.g., `uppercase=True`) into the constructors of `ReportFormatter` and `ExportManager`.
- **Priority Level**: High

---

### 5. Code Smell: Unclear/Misleading Naming & Type Shadowing
- **Problem Location**: `ReportService.generate(self, report)`
- **Detailed Explanation**: 
  ```python
  report = content # Line 73
  ```
  The variable `report` is initially passed as a `Report` object, but is then overwritten by a string (`content`). This is confusing for maintainers and breaks static type checking/IDE intellisense.
- **Improvement Suggestions**: Use a distinct variable name for the formatted string, such as `formatted_content` or `report_text`.
- **Priority Level**: Medium

---

### 6. Code Smell: Poor String Concatenation (Readability & Performance)
- **Problem Location**: `ReportFormatter.format()`
- **Detailed Explanation**: The code uses `text = text + r + "\n"`. While less severe than the character loop, it is not the idiomatic Python way to build strings from lists.
- **Improvement Suggestions**: Use a list to collect lines and then use `"\n".join(lines)`. This is more performant and readable.
- **Priority Level**: Low

---

### 7. Code Smell: Weak Abstraction/Duplicate Logic
- **Problem Location**: `TextExporter` vs `UpperTextExporter`
- **Detailed Explanation**: `UpperTextExporter` is created solely to handle a casing transformation. This logic is already partially present in `ReportFormatter`. Having separate classes for simple transformations leads to "Class Explosion."
- **Improvement Suggestions**: Remove `UpperTextExporter`. Handle the casing logic either entirely within the `ReportFormatter` or pass a transformation function/strategy to a single `TextExporter`.
- **Priority Level**: Medium

---

### Summary of Scoring & Final Thoughts
The code demonstrates a basic understanding of OOP but suffers from several "Junior-to-Mid" level mistakes—specifically regarding Python performance (string concatenation) and software architecture (global state and SRP violations).

**Top Priority Fixes:**
1. Remove the $O(n^2)$ string loop in `ReportService`.
2. Replace global `CONFIG` access with Dependency Injection.
3. Decouple `ExportManager` from concrete exporter classes.
    
    
    Linter Messages:
    ### Code Review Report

#### 1. Readability & Consistency
*   **Issue:** The codebase uses a mix of standard comments and some non-standard commentary (e.g., `❌ Refused Bequest 預備役`).
*   **Consistency:** While indentation is consistent, the spacing between logic blocks is somewhat excessive, creating fragmented readability.

#### 2. Naming Conventions
*   **Variable Clarity:** In `ReportFormatter.format`, the variable `r` is used for rows. While short, `row` would be more descriptive.
*   **Semantic Clarity:** `JsonLikeExporter` is named appropriately as it does not produce valid JSON (it uses single quotes), but the implementation is brittle.

#### 3. Software Engineering Standards
*   **Violation of LSP/ISP:** The `BaseExporter.finish()` method is an example of the "Refused Bequest" smell. Subclasses are forced to inherit a method they may not need.
*   **Violation of SRP (Single Responsibility Principle):** `ReportService.generate` is doing too much: formatting, preparing, and manually buffering characters.
*   **Tight Coupling:** `ReportFormatter` and `ExportManager` rely directly on a global `CONFIG` dictionary. This makes the code difficult to test in isolation or run in parallel with different configurations.
*   **Redundancy:** The loop in `ReportService.generate` that iterates through characters to build a `buffer` string is entirely redundant as `prepared` is already a string.

#### 4. Logic & Correctness
*   **Variable Shadowing:** In `ReportService.generate`, the line `report = content` overwrites the `report` object (an instance of `Report`) with a string. This is confusing and disrupts type consistency.
*   **String Concatenation Performance:** The code uses `text = text + r` and `buffer = buffer + ch` inside loops. In Python, this is an $O(n^2)$ operation.

#### 5. Performance & Security
*   **Inefficiency:** The manual character-by-character loop in `ReportService` is a significant performance bottleneck for large reports.
*   **Security:** `JsonLikeExporter` uses simple string concatenation for JSON-like output. This is prone to injection issues or malformed output if the data contains single quotes.

#### 6. Documentation & Testing
*   **Missing Documentation:** There are no docstrings for classes or methods.
*   **Lack of Tests:** No unit tests are provided; the logic is only verified via a `main()` execution script.

---

### Linter Messages

```json
[
  {
    "rule_id": "perf-string-concatenation",
    "severity": "warning",
    "message": "Inefficient string concatenation in loop. Use ''.join() for better performance.",
    "line": 75,
    "suggestion": "Use '\n'.join(rows) instead of a for-loop with +=."
  },
  {
    "rule_id": "logic-variable-shadowing",
    "severity": "error",
    "message": "Variable 'report' is reassigned from a Report object to a string, changing its type mid-function.",
    "line": 93,
    "suggestion": "Use a different variable name, e.g., 'formatted_content'."
  },
  {
    "rule_id": "redundant-logic",
    "severity": "warning",
    "message": "Redundant loop constructing a string from characters of an existing string.",
    "line": 98,
    "suggestion": "Remove the 'for ch in prepared' loop and pass 'prepared' directly to export()."
  },
  {
    "rule_id": "design-global-state",
    "severity": "warning",
    "message": "Direct dependency on global CONFIG dictionary hinders testability and modularity.",
    "line": 74,
    "suggestion": "Pass configuration settings as arguments to the constructor or method."
  },
  {
    "rule_id": "design-refused-bequest",
    "severity": "info",
    "message": "BaseExporter defines finish() which is not utilized by all subclasses.",
    "line": 18,
    "suggestion": "Consider moving finish() to a separate interface or removing it from the base class."
  },
  {
    "rule_id": "security-unsafe-serialization",
    "severity": "error",
    "message": "Manual string formatting used to create JSON-like structure is fragile and insecure.",
    "line": 48,
    "suggestion": "Use the 'json' standard library for serialization."
  },
  {
    "rule_id": "naming-too-short",
    "severity": "info",
    "message": "Variable name 'r' is not descriptive.",
    "line": 73,
    "suggestion": "Rename 'r' to 'row'."
  }
]
```
    
    
    Review Comment:
    First code review: 

## Code Review Report

### 1. Readability & Consistency
*   **Formatting:** The code generally follows PEP 8 indentation and spacing.
*   **Comments:** There is a comment regarding "Refused Bequest" in `BaseExporter`, but it reads like a note to self rather than professional documentation. It should be removed or rewritten as a design justification.

### 2. Naming Conventions
*   **Variable Shadowing:** In `ReportService.generate`, the variable `report` is reassigned from a `Report` object to a `content` string (`report = content`). This is confusing and breaks semantic clarity.
*   **Vague Naming:** `r` in `ReportFormatter.format` should be renamed to `row` for better descriptiveness.
*   **Naming Consistency:** `JsonLikeExporter` uses a specific naming style ("Like"), while others are generic. Consistency is acceptable here, but be mindful of naming patterns.

### 3. Software Engineering Standards
*   **Code Duplication:** `TextExporter` and `UpperTextExporter` share almost identical `export` and `finish` logic. The uppercasing logic should be handled by the `prepare` method or a decorator to avoid duplicating the `export` method.
*   **Modularity:** `ReportFormatter` is instantiated inside `ReportService.generate`. This creates a hard dependency. Consider injecting the formatter or making it a static utility.
*   **Inheritance:** `BaseExporter.finish()` is an empty method that most subclasses don't need. If it's not part of a required lifecycle, it should be removed to avoid "Interface Pollution."

### 4. Logic & Correctness
*   **Inefficient String Concatenation:** In `ReportFormatter.format` and `ReportService.generate`, strings are built using `+` in a loop. In Python, this is $O(n^2)$ and inefficient. Use `''.join()` instead.
*   **Redundant Loop:** The loop `for ch in prepared: buffer = buffer + ch` in `ReportService` simply copies the string character by character. This serves no logical purpose and should be removed.
*   **Hardcoded JSON logic:** `JsonLikeExporter` manually concatenates strings to create a JSON-like format. This is error-prone (e.g., doesn't handle escaping). Use the `json` library.

### 5. Performance & Security
*   **Complexity:** The `buffer` loop and repeated string additions in the formatter introduce unnecessary performance bottlenecks for large reports.
*   **Global State:** Reliance on a global `CONFIG` dictionary makes the code hard to test in parallel and prone to side-effect bugs. Pass configuration as parameters.

### 6. Documentation & Testing
*   **Missing Documentation:** No docstrings are provided for classes or methods.
*   **Missing Tests:** No unit tests are provided for the exporters or the formatting logic.

---

### Summary of Suggestions

| Component | Issue | Suggestion |
| :--- | :--- | :--- |
| `ReportService` | Variable Shadowing | Rename `report = content` to `formatted_content = content`. |
| `ReportService` | Redundant Loop | Remove the `for ch in prepared` loop; use `prepared` directly. |
| `ReportFormatter` | Performance | Replace `text = text + r` with a list and `''.join(rows)`. |
| `Exporters` | Duplication | Merge `UpperTextExporter` into `TextExporter` by passing a flag or using the `prepare` method. |
| `JsonLikeExporter` | Correctness | Use `import json` instead of manual string building. |
| `Global` | Architecture | Replace `CONFIG` global dictionary with a configuration object/class. |

First summary: 

This code review is conducted based on the global rules provided.

### Overall Assessment
The code implements a basic report export system using an object-oriented approach. While the structure separates concerns (Management, Service, Exporter), it suffers from several architectural anti-patterns, poor performance choices in string handling, and a lack of robust error handling.

---

### 1. Readability & Consistency
*   **Consistency:** The formatting is generally consistent, but the use of a global `CONFIG` dictionary creates "hidden" dependencies throughout the classes, making the flow hard to follow.
*   **Comments:** There is a comment mentioning "Refused Bequest" (LISP/OOP term), which is helpful for intent but indicates the author is aware of the design flaw without fixing it.

### 2. Naming Conventions
*   **General:** Variable names are mostly clear (`ReportService`, `ExportManager`).
*   **Improvement:** `r` in `ReportFormatter.format` is too short; `row` would be more descriptive.

### 3. Software Engineering Standards
*   **Violation of SRP (Single Responsibility Principle):** 
    *   `ReportFormatter` checks the global `CONFIG` to decide on casing. Formatting logic should be decoupled from configuration.
    *   `ExportManager` handles both the factory logic (`create_exporter`) and the execution logic.
*   **Violation of LSP (Liskov Substitution Principle):** `BaseExporter` defines `finish()`, but `JsonLikeExporter` does not implement it, and the base class provides a dummy `pass`. This confirms the "Refused Bequest" issue.
*   **Modularization:** The `ReportFormatter` is instantiated inside `ReportService.generate` (tight coupling). It should be injected via the constructor.

### 4. Logic & Correctness
*   **Variable Shadowing:** In `ReportService.generate`:
    ```python
    report = content # This overwrites the 'report' object with a string.
    ```
    This is dangerous and confusing. Use distinct names (e.g., `formatted_content`).
*   **Incomplete Implementation:** `ExportManager.run` calculates `duration` but does nothing with it.
*   **Fragile Factory:** The `create_exporter` method defaults to `TextExporter` for any unknown format without logging a warning or raising an error.

### 5. Performance & Security
*   **String Concatenation Bottleneck:** 
    *   In `ReportFormatter.format` and `ReportService.generate`, strings are concatenated using `+` in a loop. 
    *   **Risk:** In Python, strings are immutable. Loop-based concatenation is $O(n^2)$. 
    *   **Fix:** Use `''.join(list_of_strings)`.
*   **Security:** The `JsonLikeExporter` manually constructs a JSON string using concatenation (`"{'report': '" + data + "'}"`). This is prone to errors and security risks if `data` contains quotes. Use the `json` library.

### 6. Documentation & Testing
*   **Missing Docs:** There are no docstrings for classes or methods.
*   **Testing:** No unit tests provided. The `main()` function acts as a manual smoke test, which is insufficient for a production system.

---

### Summary of Recommendations

| Category | Issue | Priority | Suggested Fix |
| :--- | :--- | :--- | :--- |
| **Performance** | $O(n^2)$ String concatenation | High | Replace `+` loops with `.join()`. |
| **Logic** | Variable shadowing | High | Rename `report = content` in `ReportService`. |
| **Design** | Global CONFIG dependency | Medium | Pass configuration as arguments to constructors. |
| **Design** | LSP Violation | Medium | Remove `finish()` from `BaseExporter` or make it an optional Interface. |
| **Security** | Manual JSON construction | Medium | Use `import json`. |
| **Testing** | Lack of test suite | Low | Implement `pytest` or `unittest` cases. |

### Final Score: ⚠️ Needs Improvement
The code is functional for a script but lacks the rigor required for a maintainable software project. The performance and architectural issues should be addressed before merging.

Total summary: 

 ### 1. Overall Conclusion
The PR **does not meet merge criteria**. While the code is functionally operational for small scripts, it contains critical performance flaws, architectural anti-patterns, and a high-severity security risk regarding data serialization. These issues are blocking and must be addressed before the code can be considered maintainable or production-ready.

### 2. Comprehensive Evaluation
*   **Code Quality & Correctness**:
    *   **Critical Performance Failures**: The implementation contains $O(n^2)$ string concatenation patterns in both `ReportFormatter.format` and `ReportService.generate`. Specifically, `ReportService` includes a redundant character-by-character loop that serves no logical purpose and severely degrades performance for large reports.
    *   **Logic Errors**: There is blatant variable shadowing in `ReportService.generate` where a `Report` object is reassigned to a string, breaking type consistency.
    *   **Security & Reliability**: `JsonLikeExporter` manually constructs "JSON" using string concatenation. This is fragile and prone to malformed output or injection if the data contains quotes; it violates standard serialization practices.
*   **Maintainability & Design**:
    *   **Tight Coupling & Global State**: Widespread reliance on a global `CONFIG` dictionary obscures dependencies and prevents parallel testing or modular configuration.
    *   **Architectural Smells**:
        *   **LSP Violation**: `BaseExporter.finish()` is a "Refused Bequest," forced upon subclasses that do not need it.
        *   **SRP Violation**: `ExportManager` conflates factory logic (instantiation) with execution logic.
        *   **Class Explosion**: `UpperTextExporter` duplicates logic that could be handled by a strategy or a flag within `TextExporter`.
    *   **Hard-coded Dependencies**: `ReportFormatter` is instantiated directly inside `ReportService`, preventing the use of mock formatters for testing.
*   **Consistency & Documentation**:
    *   **Missing Essentials**: There are no docstrings or unit tests. Verification relies solely on a manual `main()` smoke test.
    *   **Naming**: Variable naming is generally acceptable, though `r` in the formatter is too brief.

### 3. Final Decision Recommendation
**Decision: Request Changes**

**Justification**:
The PR contains several "High" priority issues that compromise the stability and scalability of the system:
1.  **Performance**: $O(n^2)$ string building must be replaced with `.join()`.
2.  **Security**: Manual JSON construction must be replaced with the `json` library.
3.  **Architecture**: Global state (`CONFIG`) and tight coupling must be replaced with Dependency Injection.
4.  **Correctness**: Variable shadowing and redundant loops must be removed.

### 4. Team Follow-up
*   **Refactor String Handling**: Audit all loops involving string concatenation and implement `list.append()` followed by `''.join()`.
*   **Implement Dependency Injection**: Update `ReportFormatter` and `ExportManager` to accept configuration parameters in their constructors.
*   **Apply Factory Pattern**: Move exporter creation logic out of `ExportManager` into a dedicated factory or registry.
*   **Standardize Serialization**: Ensure all structured data exports use approved libraries (e.g., `json`) rather than manual string formatting.
*   **Add Test Suite**: Implement unit tests for all exporters and the `ReportService` logic.

Step by step analysis: 

Since you have provided a comprehensive set of Linter Results and Code Smell analyses, I will now perform the deep-dive review as the Code Quality Reviewer, analyzing the most critical issues step-by-step according to your required instructions.

---

### 1. Performance: Inefficient String Concatenation
**Linter Message:** `perf-string-concatenation: Inefficient string concatenation in loop. Use ''.join() for better performance.`

**1. Identify the Issue**
The code uses the `+` operator to append strings inside a loop (e.g., `text = text + r`). In software engineering, this is known as "Quadratic String Building."

**2. Root Cause Analysis**
Strings in Python are immutable. Every time you use `+` to add a character or string, Python must allocate a completely new memory block and copy the entire old string into it along with the new content.

**3. Impact Assessment**
*   **Performance:** As the report size grows, the time taken to generate it increases exponentially ($O(n^2)$). For large files, this can cause the application to hang or timeout.
*   **Severity:** **High** (Performance Bottleneck).

**4. Suggested Fix**
Collect all strings in a list and join them once at the end.
```python
# Bad
text = ""
for r in rows:
    text = text + r + "\n"

# Good
lines = []
for r in rows:
    lines.append(r)
text = "\n".join(lines)
```

**5. Best Practice Note**
**Idiomatic Python:** Always prefer `.join()` for aggregating sequences of strings. It calculates the total required memory once, making it $O(n)$.

---

### 2. Logic: Variable Type Shadowing
**Linter Message:** `logic-variable-shadowing: Variable 'report' is reassigned from a Report object to a string, changing its type mid-function.`

**1. Identify the Issue**
A variable named `report` is used to hold a complex object (the `Report` instance) but is later reassigned to hold a simple string (the content of the report).

**2. Root Cause Analysis**
This occurs due to poor naming hygiene and a lack of distinct variables for different stages of data transformation (input $\rightarrow$ processed $\rightarrow$ output).

**3. Impact Assessment**
*   **Maintainability:** It confuses developers. Someone reading the code might attempt to call a method of the `Report` class on the `report` variable, only to find it is now a string, causing a `AttributeError` crash.
*   **Tooling:** It breaks static type checkers (like Mypy) and IDE autocomplete.
*   **Severity:** **Medium**.

**4. Suggested Fix**
Use descriptive names that reflect the state of the data.
```python
# Bad
def generate(self, report):
    report = content # Overwrites the object with a string

# Good
def generate(self, report_obj):
    formatted_content = self.formatter.format(report_obj)
```

**5. Best Practice Note**
**Type Consistency:** Variables should maintain a consistent type throughout their scope. If the data type changes, use a new variable name.

---

### 3. Architecture: Refused Bequest
**Code Smell:** `BaseExporter defines finish() which is not utilized by all subclasses.`

**1. Identify the Issue**
A base class forces its children to inherit a method (`finish()`) that they do not actually need. The child classes either leave it empty or ignore it entirely.

**2. Root Cause Analysis**
This is a design flaw where the base class is "too fat." It assumes all exporters will need a cleanup/finish phase, regardless of whether they are writing to a database, a file, or just returning a string.

**3. Impact Assessment**
*   **Readability:** It creates "dead code" in subclasses.
*   **LSP Violation:** It violates the **Liskov Substitution Principle**, as the base class contract promises a behavior that the subclasses don't meaningfully implement.
*   **Severity:** **Low/Medium**.

**4. Suggested Fix**
Remove the method from the base class. If only specific exporters need it, create a Mixin or a more specific interface.
```python
# Better Approach: Interface Segregation
class BaseExporter:
    def export(self, data): pass

class FileExporter(BaseExporter, IDisposable):
    def export(self, data): ...
    def finish(self): # Only defined where it's actually needed
        self.file.close()
```

**5. Best Practice Note**
**Interface Segregation Principle (ISP):** No client should be forced to depend on methods it does not use. Keep interfaces lean and focused.

---

### 4. Security: Unsafe Serialization
**Linter Message:** `security-unsafe-serialization: Manual string formatting used to create JSON-like structure is fragile and insecure.`

**1. Identify the Issue**
The `JsonLikeExporter` manually wraps data in quotes (e.g., `'{ 'key': 'value' }'`) instead of using a standard library.

**2. Root Cause Analysis**
The developer tried to save time by using string templates rather than employing a formal serialization library.

**3. Impact Assessment**
*   **Security:** If the data contains single quotes, the output will be malformed. If the data comes from a user, it could lead to "Injection" attacks where the output structure is manipulated.
*   **Reliability:** The output is "JSON-like" but not valid JSON, making it incompatible with standard API tools.
*   **Severity:** **High**.

**4. Suggested Fix**
Use the standard `json` library.
```python
import json

# Bad: manual string concatenation
# return f"{{'data': '{content}'}}"

# Good: Proper serialization
return json.dumps({"data": content})
```

**5. Best Practice Note**
**Don't Reinvent the Wheel:** Always use standard, battle-tested libraries for data serialization (JSON, XML, YAML) to ensure security and spec compliance.
    
    
    You should first generate a step-by-step list
    of all the topics the review should cover like
    code smells, issues that would be flagged by a
    linter, security vulnerabilities, etc. Also,
    the review should cover aspects like bugs, code
    security, code readability, maintainability,
    memory consumption, performance, good and bad
    design patterns, and efficiency introduced in
    the code change. Put your analysis under a
    section titled \### Topics to be Covered:".
    
    After generating the list above you should
    again think step-by-step about the given review
    comment and whether it addresses these topics
    and put it under a section called "###
    Step-by-Step Analysis of Review Comment:". Then
    based on your step-by-step analysis you should
    generate a score ranging from 1 (minimum value)
    to 5 (maximum value) each about how
    comprehensive, concise, and relevant a review
    is. A review getting a score of 5 on
    comprehensiveness addresses nearly all the
    points in the \### Topics to be Covered:"
    section while a review scoring 1 addresses none
    of them. A review getting a score of 5 on
    conciseness only covers the topics in the \###
    Topics to be Covered:" section without wasting
    time on off-topic information while a review
    getting a score of 1 is entirely off-topic.
    Finally, a review scoring 5 on relevance is
    both concise and comprehensive while a review
    scoring 1 is neither concise nor comprehensive,
    effectively making relevance a combined score
    of conciseness and comprehensiveness. You
    should give your final rating in a section
    titled \### Final Scores:". give the final scores as shown
    below (please follow the exact format).
    
    ### Final Scores:
    ```
    ("comprehensiveness": your score, "conciseness": your score,
    "relevance": your score)
    ```
    Now start your analysis starting with the \###
    Topics to be Covered:", followed by "###
    Step-by-Step Analysis of Review Comment:" and
    ending with the \### Final Scores:".
    
    ### Topics to be Covered:
    (topics_to_be_covered)
