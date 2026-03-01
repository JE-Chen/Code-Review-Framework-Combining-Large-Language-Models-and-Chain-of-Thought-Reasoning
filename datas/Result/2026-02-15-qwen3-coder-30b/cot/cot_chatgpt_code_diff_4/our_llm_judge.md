
# Code Review Comment Evaluation Template

Please evaluate the review comments using the following scoring mechanism.  
Focus on whether the comments effectively help improve the code, especially by leveraging code smell and linter messages.

Score range: 1–100

Six evaluation dimensions:
1. Readability
    - 1–20: Comments are very hard to understand, poorly structured, confusing language.
    - 21–40: Some parts are readable, but many unclear sections remain.
    - 41–60: Comments are generally clear, but structure or phrasing needs improvement.
    - 61–80: Comments are well-structured, consistent, and easy to follow.
    - 81–100: Comments are highly readable, elegantly phrased, and well-organized.

2. Constructiveness (Maintainability)
    - 1–20: Comments lack constructive suggestions, no improvement direction.
    - 21–40: Comments provide partial suggestions, but vague or impractical.
    - 41–60: Comments offer basic improvement ideas, somewhat helpful.
    - 61–80: Comments are specific and actionable, clearly guiding improvements.
    - 81–100: Comments are highly constructive, offering clear and practical improvement paths.

3. Correctness
    - 1–20: Comments contain errors or misleading advice.
    - 21–40: Mostly correct, but important issues are overlooked.
    - 41–60: Largely correct, with only minor gaps.
    - 61–80: Correct and reasonable, with small room for refinement.
    - 81–100: Fully correct, logically sound, and precise in identifying issues.

4. Conciseness
    - 1–20: Comments are overly long, irrelevant to code improvement.
    - 21–40: Some relevant points, but too much unnecessary content.
    - 41–60: About half of the comments are focused and relevant.
    - 61–80: Most comments are concise and focused on improvement.
    - 81–100: All comments are precise, concise, and directly related to improvement.

5. Comprehensiveness
    - 1–20: Comments fail to address any code smells or linter findings.
    - 21–40: Comments mention at least one code smell or linter warning.
    - 41–60: Comments cover some code smells or linter findings.
    - 61–80: Comments cover most code smells and linter findings.
    - 81–100: Comments comprehensively address all code smells and linter findings, with improvement suggestions.

6. Relevance
    Relevance = (2 * Conciseness * Comprehensiveness) / (Conciseness + Comprehensiveness)

Reviewers should:
- Assign a score (1–100) for each dimension.
- Provide brief reasoning for each score.
- Conclude with an average score and overall recommendation.

## Review Comment:
First code review: 

- **Readability & Formatting**  
  - Indentation is consistent but could benefit from aligning multi-line SQL strings for better readability.  
  - Comments are missing; consider adding brief docstrings or inline comments for key functions like `write_log` and `do_business_logic_but_sql_heavy`.

- **Naming Conventions**  
  - Function name `do_business_logic_but_sql_heavy` is unclear and verbose — rename to something more descriptive such as `simulate_user_activity`.  
  - Variables like `i`, `ts`, `msg` are acceptable but can be expanded slightly for clarity (e.g., `log_id`, `timestamp`, `message_text`) in contexts where ambiguity might occur.

- **Modularity & Maintainability**  
  - Hardcoded values (`3`, `LIMIT`, etc.) should be extracted into constants or parameters to improve reusability and testing.  
  - The use of global connection (`CONN`, `CURSOR`) reduces modularity and makes testing harder. Consider passing dependencies explicitly.

- **Logic & Correctness**  
  - SQL injection vulnerability exists in both `write_log` and `read_logs` due to string concatenation instead of parameterized queries.  
  - In `do_business_logic_but_sql_heavy`, unhandled exceptions during commit may hide real failures; logging or raising would improve error visibility.  
  - Randomized behavior in `write_log` and `do_business_logic_but_sql_heavy` introduces inconsistency — make it deterministic for easier debugging and testing.

- **Performance & Security**  
  - Frequent commits inside loops (e.g., in `write_log`) can reduce performance. Committing once after batch operations is preferred.  
  - Using `:memory:` database is fine for demo, but production code should validate and manage DB connections properly.

- **Documentation & Testing**  
  - No docstrings or type hints present. Adding them improves maintainability and understanding.  
  - Lack of unit tests for core logic increases risk of regressions. Suggest mocking the DB and validating outputs.

- **Suggestions**  
  - Replace raw SQL with parameterized queries in `write_log` and `read_logs`.  
  - Extract hardcoded numbers and strings into named constants.  
  - Rename `do_business_logic_but_sql_heavy` for clarity.  
  - Make `setup()` and `main()` more testable by accepting config or DB connection.  
  - Use `try...except` with specific exception types instead of bare `except`.

First summary: 

### ✅ Summary

#### Key Changes
- Introduces a basic logging application using SQLite in-memory database.
- Implements functions for setting up logs, writing log entries, reading logs, and simulating business logic with SQL-heavy operations.

#### Impact Scope
- Affects `db_app.py` as the only new module.
- Uses in-memory SQLite (`:memory:`), which limits persistence and scalability.

#### Purpose of Changes
- Demonstrates a simple data access layer with simulated workload.
- Likely used for prototyping or educational purposes.

#### Risks and Considerations
- Insecure SQL string concatenation in `write_log()` may lead to injection vulnerabilities.
- Randomized commit behavior introduces inconsistency.
- No error handling beyond silent exceptions.

#### Items to Confirm
- Review SQL injection risk in `write_log`.
- Evaluate necessity of random commits and query limits.
- Confirm expected behavior for in-memory DB usage.

---

### 🧠 Code Review Feedback

#### 1. **Readability & Consistency**
- ✅ Indentation and structure are clean.
- ⚠️ Comments are missing; consider adding inline comments explaining purpose of key logic blocks.
- 💡 Formatting is consistent but could benefit from PEP8 linting enforcement.

#### 2. **Naming Conventions**
- ✅ Function and variable names are clear and descriptive.
- 💡 Slight improvement: rename `do_business_logic_but_sql_heavy()` to something like `simulate_logging_workload()` for better clarity.

#### 3. **Software Engineering Standards**
- ❌ Duplicated logic: `read_logs()` builds a formatted output list — this can be extracted into helper functions.
- ⚠️ Magic numbers: hardcoded values like `3`, `5`, etc., should be constants.
- 🔁 Refactor repeated pattern of fetching logs with optional limit into reusable utility.

#### 4. **Logic & Correctness**
- ❌ **SQL Injection Risk**: Using f-strings directly in SQL queries (`f"INSERT INTO logs ..."`).
  - ✅ Fix by parameterizing queries:  
    ```python
    CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
    ```
- ⚠️ Unreliable commits: `random.choice([True, False])` makes transaction state unpredictable.
- ⚠️ Silent catch-all exception (`except Exception`) hides errors silently.

#### 5. **Performance & Security**
- ⚠️ In-memory DB use is fine for demo, but not production-grade.
- ⚠️ Frequent small writes without batching may hurt performance.
- ❌ No input sanitization or validation.

#### 6. **Documentation & Testing**
- ❌ Missing docstrings for functions.
- ❌ No unit tests provided — critical for verifying correctness of `write_log`, `read_logs`, and `do_business_logic_but_sql_heavy`.

#### 7. **Scoring Breakdown**
| Category                | Score |
|------------------------|-------|
| Readability & Consistency | ⭐⭐⭐⭐ |
| Naming Conventions      | ⭐⭐⭐⭐ |
| Software Engineering    | ⭐⭐⭐ |
| Logic & Correctness     | ⭐⭐ |
| Performance & Security  | ⭐⭐ |
| Documentation & Tests   | ⭐⭐ |

---

### 🛠 Recommendations
1. Use parameterized queries instead of string formatting.
2. Add docstrings and type hints.
3. Replace magic numbers with named constants.
4. Avoid silent exception handling.
5. Test edge cases such as empty results or invalid inputs.

---

### ✅ Final Notes
This is a functional prototype with room for major improvements in safety, modularity, and maintainability. Prioritize fixing SQL injection risks before merging.

Total summary: 

 - **Overall Conclusion**  
  The PR does **not meet merge criteria** due to several **high-severity issues** including SQL injection vulnerabilities, poor error handling, and global state misuse. While some low-severity concerns exist, critical flaws must be addressed before merging.

- **Comprehensive Evaluation**  
  - **Code Quality & Correctness**: The implementation contains unsafe SQL string interpolation in `write_log`, leading to potential injection risks. Silent exception handling in `do_business_logic_but_sql_heavy` hides operational failures. Inconsistent commit behavior undermines data integrity.
  - **Maintainability & Design**: Global variables (`CONN`, `CURSOR`) reduce modularity and testability. Magic numbers and hardcoded strings decrease clarity. Business logic is tightly coupled with database access.
  - **Consistency**: Code style is generally consistent, but lacks documentation, type hints, and standard Python idioms (e.g., no use of `const` or structured classes).

- **Final Decision Recommendation**  
  ❌ **Request changes**  
  Core issues like SQL injection, improper exception handling, and tight coupling must be resolved. Addressing these will improve robustness, security, and maintainability.

- **Team Follow-Up**  
  - Refactor `write_log` and `read_logs` to use parameterized queries.
  - Replace global DB state with injected dependencies.
  - Extract constants for magic numbers and strings.
  - Implement proper logging or raising of exceptions instead of silent catches.
  - Consider moving logic into a class structure to enhance testability.

Step by step analysis: 

### 1. **Global Variable Reassignment (`no-global-assign`)**
- **Issue**: The variables `CONN` and `CURSOR` are assigned at the global scope and reassigned later.
- **Explanation**: This breaks encapsulation and makes the code harder to reason about. Global state is hard to track and manage.
- **Why it's bad**: Can cause unintended side effects, especially during parallel execution or testing.
- **Fix**: Avoid modifying global variables. Use local or injected dependencies instead.
```javascript
// Instead of:
CONN = sqlite3.connect("example.db");

// Prefer:
function createConnection() {
  return sqlite3.connect("example.db");
}
```

---

### 2. **Unnecessary Escape Sequences (`no-useless-escape`)**
- **Issue**: Escaping parentheses in strings like `'\\('` has no effect.
- **Explanation**: The backslash does not need escaping in regular strings unless followed by special characters.
- **Why it's bad**: Confusing and unnecessary; reduces readability.
- **Fix**: Remove unneeded escapes.
```javascript
// Before:
const sql = "SELECT * FROM logs WHERE id = \\(1\\)";

// After:
const sql = "SELECT * FROM logs WHERE id = (1)";
```

---

### 3. **Duplicate Object Keys (`no-duplicate-key`)**
- **Issue**: Duplicate keys in an object literal (`ts` appears twice).
- **Explanation**: Only one value will be used, hiding possible bugs.
- **Why it's bad**: Leads to silent data loss or confusion.
- **Fix**: Ensure all keys are unique.
```javascript
// Before:
{ ts: 123, ts: 456 }

// After:
{ ts: 123, timestamp: 456 }
```

---

### 4. **Unreachable Code (`no-unreachable`)**
- **Issue**: Code after a `return` statement is unreachable.
- **Explanation**: Likely leftover from debugging or refactoring.
- **Why it's bad**: Wastes space and confuses readers.
- **Fix**: Remove or refactor.
```javascript
// Before:
if (condition) return;
console.log("unreachable"); // unreachable

// After:
if (condition) return;
```

---

### 5. **Empty Block Statements (`no-empty-blocks`)**
- **Issue**: An empty block exists without purpose.
- **Explanation**: May indicate incomplete logic or dead code.
- **Why it's bad**: Misleading and confusing.
- **Fix**: Either implement logic or delete the block.
```javascript
// Before:
try { } catch (err) {}

// After:
try {
  // handle logic
} catch (err) {
  console.error(err);
}
```

---

### 6. **Magic Numbers (`no-magic-numbers`)**
- **Issue**: Direct use of numeric literals like `3`, `5`, `0.2`.
- **Explanation**: Not self-documenting; makes maintenance harder.
- **Why it's bad**: Difficult to update or explain.
- **Fix**: Replace with named constants.
```javascript
// Before:
if (count > 3) ...

// After:
const MAX_RETRY_COUNT = 3;
if (count > MAX_RETRY_COUNT) ...
```

---

### 7. **Use of `var` Instead of `let`/`const` (`no-var`)**
- **Issue**: Declaring variables with `var` instead of modern alternatives.
- **Explanation**: `var` has function-scoped scope, unlike `let`/`const`.
- **Why it's bad**: Leads to scoping issues and unexpected behavior.
- **Fix**: Prefer `let` or `const`.
```javascript
// Before:
var x = 1;

// After:
const x = 1;
```

---

### 8. **Implicit Global Variables (`no-implicit-globals`)**
- **Issue**: Variables declared without explicit keyword (`var`, `let`, `const`).
- **Explanation**: Automatically becomes global, causing pollution.
- **Why it's bad**: Increases chance of naming collisions.
- **Fix**: Always declare with `let` or `const`.
```javascript
// Before:
CONN = sqlite3.connect(...);

// After:
const CONN = sqlite3.connect(...);
```

---

### 9. **SQL Injection Risk**
- **Issue**: Building SQL via string interpolation.
- **Explanation**: Enables attackers to manipulate queries.
- **Why it's bad**: Security vulnerability.
- **Fix**: Use parameterized queries.
```javascript
// Before:
const sql = `INSERT INTO logs VALUES ('${msg}')`;

// After:
const sql = "INSERT INTO logs VALUES (?)";
CURSOR.execute(sql, [msg]);
```

---

### 10. **Poor Error Handling**
- **Issue**: Silent exception handling (`except Exception:`).
- **Explanation**: Errors go unnoticed.
- **Why it's bad**: Makes debugging difficult.
- **Fix**: Log or re-raise errors.
```javascript
// Before:
try:
    CURSOR.execute(...)
except Exception:
    pass

// After:
try:
    CURSOR.execute(...)
except Exception as e:
    print(f"Database error: {e}")
    raise
```

---

### 11. **Lack of Input Validation**
- **Issue**: No checks on input message length or type.
- **Explanation**: Can cause crashes or data integrity issues.
- **Fix**: Validate input early.
```javascript
if (typeof msg !== "string" || msg.length > 1000) {
  throw new Error("Invalid message");
}
```

---

### 12. **Tight Coupling Between Logic and DB**
- **Issue**: Business logic mixed with raw SQL calls.
- **Explanation**: Makes testing and modification hard.
- **Fix**: Separate concerns.
```javascript
class LoggerService {
  constructor(db) {
    this.db = db;
  }

  writeLog(msg) {
    const sql = "INSERT INTO logs VALUES (?)";
    this.db.execute(sql, [msg]);
  }
}
```

---

### 13. **Formatting Inside Data Retrieval**
- **Issue**: Formatting done in `read_logs()`.
- **Explanation**: Violates separation of concerns.
- **Fix**: Return clean data.
```javascript
// Before:
logs.map(log => `${log.timestamp}: ${log.message}`)

// After:
logs.map(log => ({ timestamp: log.timestamp, message: log.message }))
```

---

### 14. **Inconsistent Transaction Commit Behavior**
- **Issue**: Random commit decisions.
- **Explanation**: Inconsistent state management.
- **Fix**: Explicitly control commit behavior.
```javascript
if (shouldCommit) {
  CONN.commit();
}
```

---

### 15. **Lack of Modularity**
- **Issue**: All logic lives at module level.
- **Explanation**: Hard to test and reuse.
- **Fix**: Encapsulate in classes.
```javascript
class DatabaseManager {
  constructor(path) {
    this.conn = sqlite3.connect(path);
  }
}
```

---

### 16. **Hardcoded Delays**
- **Issue**: Fixed sleep time (`0.2` seconds).
- **Explanation**: Not flexible or portable.
- **Fix**: Make configurable.
```javascript
const DELAY_MS = 200;
await new Promise(resolve => setTimeout(resolve, DELAY_MS));
```

---

### Summary of Key Fixes:
| Rule | Problem | Suggested Action |
|------|---------|------------------|
| `no-global-assign` | Global reassignment | Use locals or injectors |
| `no-useless-escape` | Escaped chars | Remove unnecessary escapes |
| `no-duplicate-key` | Duplicate keys | Rename conflicting keys |
| `no-unreachable` | Dead code | Remove unreachable blocks |
| `no-empty-blocks` | Empty blocks | Implement or remove |
| `no-magic-numbers` | Magic numbers | Replace with named constants |
| `no-var` | Use of `var` | Switch to `let` or `const` |
| `no-implicit-globals` | Implicit globals | Declare explicitly |
| `no-sql-injection` | Unsafe SQL | Use parametrized queries |
| `no-poor-error-handling` | Silenced errors | Log or re-raise |
| `no-input-validation` | No input checks | Validate inputs |
| `no-tight-coupling` | Mixed logic/db | Separate concerns |
| `no-formatting-in-retrieval` | Inline formatting | Return raw data |
| `no-random-commit` | Inconsistent commits | Make explicit |
| `no-modularity` | Flat structure | Modularize into classes |
| `no-hardcoded-delay` | Fixed sleeps | Configurable delays |

By addressing these points, your code improves in terms of correctness, testability, and long-term maintainability.

## Code Smells:
---

### Code Smell Type: Global State Dependency
- **Problem Location:** `CONN` and `CURSOR` defined at module level.
- **Detailed Explanation:** The use of global variables (`CONN`, `CURSOR`) makes the code tightly coupled to a fixed database instance. This hinders modularity, testability, and reuse. It also introduces hidden dependencies that can lead to race conditions or unexpected behavior when running multiple instances or in concurrent environments.
- **Improvement Suggestions:** Encapsulate database access within classes or functions that accept connections as parameters. Use dependency injection where applicable.
- **Priority Level:** High

---

### Code Smell Type: SQL Injection Vulnerability
- **Problem Location:** In `write_log()` function — string interpolation into SQL query without sanitization.
- **Detailed Explanation:** Using f-strings to build SQL queries exposes the application to SQL injection attacks. Even if this is a demo, such patterns are dangerous and should never be used in production.
- **Improvement Suggestions:** Replace direct string concatenation with parameterized queries using placeholders like `?` in SQLite.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers and Strings
- **Problem Location:** 
  - `"init-{i}"` in `setup()`  
  - Random choices in `do_business_logic_but_sql_heavy()`  
  - Hardcoded limits and intervals in `read_logs()` and `main()`
- **Detailed Explanation:** These values lack semantic meaning and make code harder to understand and change. They reduce flexibility and increase risk of inconsistencies.
- **Improvement Suggestions:** Extract constants or configuration options for these values. Define enums or named constants for repeated strings and numbers.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** Empty `except Exception:` block in `do_business_logic_but_sql_heavy()`.
- **Detailed Explanation:** Catching exceptions and silently ignoring them hides real issues, making debugging difficult. It could mask failures in transaction commits or other critical operations.
- **Improvement Suggestions:** Log errors appropriately or re-raise them after inspection. At minimum, log what went wrong instead of doing nothing.
- **Priority Level:** High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** `write_log()` accepts any message string without validation.
- **Detailed Explanation:** No checks on input size, format, or content may result in malformed data or performance degradation due to oversized messages.
- **Improvement Suggestions:** Add validation for message length and type. Sanitize inputs before insertion.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between Business Logic and DB Access
- **Problem Location:** `do_business_logic_but_sql_heavy()` mixes business logic with raw DB calls.
- **Detailed Explanation:** Mixing concerns reduces testability and increases complexity. This violates the separation of concerns principle.
- **Improvement Suggestions:** Separate domain logic from persistence logic. Abstract away DB interactions behind service layers.
- **Priority Level:** High

---

### Code Smell Type: Unnecessary Complexity in Formatting
- **Problem Location:** List comprehension in `read_logs()` returns formatted strings.
- **Detailed Explanation:** Formatting logic embedded inside data retrieval obscures responsibilities. It’s better to keep formatting separate for clarity and reuse.
- **Improvement Suggestions:** Return raw data from `read_logs()` and format it externally. Consider creating a dedicated formatter utility.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Use of Commit Behavior
- **Problem Location:** `write_log()` conditionally commits based on random choice.
- **Detailed Explanation:** This unpredictable behavior makes transactions unreliable and hard to reason about. It can lead to partial writes or inconsistent state.
- **Improvement Suggestions:** Make commit strategy explicit and deterministic. Either always commit or never commit unless explicitly requested.
- **Priority Level:** High

---

### Code Smell Type: Lack of Modularity and Testability
- **Problem Location:** All functions are top-level, no clear structure or encapsulation.
- **Detailed Explanation:** Without classes or modules, testing becomes challenging. Unit tests cannot isolate components effectively.
- **Improvement Suggestions:** Refactor into a class-based architecture where each responsibility is encapsulated. Provide mockable interfaces for testing.
- **Priority Level:** Medium

---

### Code Smell Type: Redundant Operations
- **Problem Location:** `try/except` block around `CONN.commit()` in `do_business_logic_but_sql_heavy()`.
- **Detailed Explanation:** If `commit()` fails due to an already-committed transaction, catching it silently is likely incorrect usage rather than a valid error case.
- **Improvement Suggestions:** Remove redundant try-except or handle the correct failure modes properly.
- **Priority Level:** Medium

---

### Code Smell Type: Hardcoded Time Delays
- **Problem Location:** `time.sleep(0.2)` in `main()`.
- **Detailed Explanation:** Hardcoded delays make timing assumptions brittle and reduce portability. Could interfere with automated testing or real-world performance expectations.
- **Improvement Suggestions:** Allow delay to be configurable or removed entirely in favor of event-driven execution or proper async support.
- **Priority Level:** Low

---

### Summary Table:

| Code Smell Type                         | Priority |
|----------------------------------------|----------|
| Global State Dependency                | High     |
| SQL Injection Vulnerability            | High     |
| Magic Numbers and Strings              | Medium   |
| Poor Error Handling                    | High     |
| Lack of Input Validation               | Medium   |
| Tight Coupling Between Logic & DB      | High     |
| Inconsistent Use of Commit Behavior    | High     |
| Lack of Modularity and Testability     | Medium   |
| Redundant Operations                   | Medium   |
| Hardcoded Time Delays                  | Low      |

--- 

This review identifies key areas needing improvement while respecting the intent of the original code. Prioritizing high-severity issues will significantly improve reliability, maintainability, and scalability.

## Linter Messages:
```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Unexpected assignment to global variable 'CONN'. Global variables should not be reassigned.",
    "line": 7,
    "suggestion": "Use a local connection or ensure this is intentional and documented."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Unexpected assignment to global variable 'CURSOR'. Global variables should not be reassigned.",
    "line": 8,
    "suggestion": "Use a local cursor or ensure this is intentional and documented."
  },
  {
    "rule_id": "no-useless-escape",
    "severity": "warning",
    "message": "Unnecessary escape sequence '\\(' in string literal.",
    "line": 23,
    "suggestion": "Remove unnecessary escape sequences."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'ts' in object literal.",
    "line": 25,
    "suggestion": "Ensure unique keys in object literals."
  },
  {
    "rule_id": "no-unreachable",
    "severity": "warning",
    "message": "Unreachable code after return statement.",
    "line": 39,
    "suggestion": "Remove unreachable code."
  },
  {
    "rule_id": "no-empty-blocks",
    "severity": "warning",
    "message": "Empty block statement.",
    "line": 39,
    "suggestion": "Add meaningful logic or remove the block."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 3 used directly in code.",
    "line": 15,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 5 used directly in code.",
    "line": 19,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 0.2 used directly in code.",
    "line": 47,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-var",
    "severity": "warning",
    "message": "Use of 'var' instead of 'let' or 'const'.",
    "line": 21,
    "suggestion": "Prefer 'let' or 'const' over 'var'."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Implicit global variable 'CONN' declared outside of any function.",
    "line": 7,
    "suggestion": "Declare global variables explicitly using 'var', 'let', or 'const'."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Implicit global variable 'CURSOR' declared outside of any function.",
    "line": 8,
    "suggestion": "Declare global variables explicitly using 'var', 'let', or 'const'."
  }
]
```

## Origin code



