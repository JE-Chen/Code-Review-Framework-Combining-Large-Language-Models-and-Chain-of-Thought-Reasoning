rule_docs = [

# =========================
# Mutable / State Bugs
# =========================

# 【可變預設參數問題】
# 用 list / dict 當函式預設參數，會導致多次呼叫共享同一份狀態
"""
Avoid using mutable default arguments in function definitions, such as lists or dictionaries.
In Python, default arguments are evaluated only once at function definition time, not each time
the function is called. This can cause unexpected shared state between function calls.
Instead, use None as the default value and create the mutable object inside the function.
""",

# 【全域或類別層級的可變共享狀態】
# 容易造成隱性耦合，讓程式行為難以推理與測試
"""
Be careful with shared mutable state at the module or class level.
Global lists, dictionaries, or class attributes that are mutated can introduce hidden coupling
between different parts of the code and make behavior difficult to reason about or test.
Prefer passing state explicitly or encapsulating it in well-defined objects.
""",

# 【修改輸入參數的副作用】
# 函式偷偷改 caller 傳進來的資料，常造成難追的 bug
"""
Avoid modifying input arguments unless it is clearly documented and expected.
Functions that mutate their inputs can lead to surprising side effects for callers.
If mutation is required for performance reasons, document it clearly or return a new value instead.
""",

# =========================
# Control Flow & Logic
# =========================

# 【過度巢狀的條件判斷】
# 巢狀過深代表責任過多，或缺乏 early return
"""
Avoid deeply nested conditional logic, as it reduces readability and increases cognitive load.
Deep nesting often indicates that the function is doing too much or missing early returns.
Refactor complex conditionals into smaller functions or use guard clauses to simplify control flow.
""",

# 【過度依賴 truthy / falsy 判斷】
# 對 None、0、空容器特別容易出錯
"""
Do not rely on implicit truthiness for complex objects or return values.
Explicit comparisons improve readability and reduce the risk of subtle bugs,
especially when dealing with empty containers, zero values, or None.
""",

# 【捕捉過於寬泛的例外】
# except Exception 會把真正的 bug 吞掉
"""
Avoid catching broad exceptions such as `except Exception:` unless absolutely necessary.
Catching broad exceptions can hide real bugs and make debugging difficult.
Catch specific exception types and handle them intentionally.
""",

# =========================
# API & Interface Design
# =========================

# 【單一職責原則違反】
# 一個函式同時做 validation / business logic / I/O
"""
Functions and methods should have a single, clear responsibility.
If a function performs validation, transformation, and I/O at the same time,
it becomes harder to test and reuse. Split responsibilities into smaller, focused functions.
""",

# 【介面行為不透明】
# 行為依賴 hidden flag、global state 或隱性上下文
"""
Design function interfaces to be explicit and predictable.
Avoid functions whose behavior changes significantly based on hidden flags,
global variables, or implicit context. Prefer explicit parameters and clear return values.
""",

# 【回傳型別不一致】
# 呼叫端必須一直猜型別，runtime error 溫床
"""
Avoid returning different types from the same function depending on conditions.
Inconsistent return types increase the burden on callers and are a common source of runtime errors.
""",

# =========================
# Performance & Scalability
# =========================

# 【在 loop 中做重複或昂貴運算】
# 常見效能地雷，且通常可輕易重構
"""
Avoid unnecessary work inside loops, especially repeated computations or I/O operations.
Move invariant calculations outside loops and cache results when appropriate
to improve performance and readability.
""",

# 【用 comprehension 做副作用】
# list comprehension 不該用來執行邏輯
"""
Be cautious when using list comprehensions or generator expressions for side effects.
They are intended for building collections, not for executing logic.
Use explicit loops when side effects are required.
""",

# 【效能風險提醒（非過度最佳化）】
# 提醒明顯的 O(n^2)、熱路徑問題
"""
Avoid premature optimization, but be aware of obvious performance pitfalls,
such as quadratic loops over large data sets or repeated conversions inside hot paths.
""",

# =========================
# Readability & Maintainability
# =========================

# 【命名不清楚】
# 變數或函式名稱無法表達意圖
"""
Prefer clear and descriptive variable and function names over short or ambiguous ones.
Names should reflect intent, not implementation details, to make the code self-explanatory.
""",

# 【Magic number / hard-coded 值】
# 可讀性與可維護性差
"""
Avoid magic numbers and hard-coded constants scattered throughout the code.
Use named constants or configuration values to improve readability and maintainability.
""",

# 【註解在解釋「做什麼」而不是「為什麼」】
# 代表程式本身不夠清楚
"""
Comments should explain why the code exists, not what it does.
If the code requires extensive comments to explain basic logic,
it may be a sign that the code should be refactored.
""",

# =========================
# Testing & Reliability
# =========================

# 【難以測試的設計】
# 強耦合、隱性依賴、濫用 global
"""
Code should be written with testability in mind.
Tightly coupled code, hidden dependencies, and heavy use of globals
make unit testing difficult and brittle.
""",

# 【時間 / 環境相依邏輯未抽象】
# 會讓測試變得不穩定
"""
Avoid time-dependent or environment-dependent logic without proper abstraction.
Direct calls to system time, random number generators, or environment variables
should be isolated to make tests deterministic.
""",

# =========================
# Security & Robustness
# =========================

# 【未驗證外部輸入】
# 安全與穩定性風險
"""
Never trust external input without validation.
Inputs from users, files, or network sources should be validated and sanitized
before being used in business logic or database operations.
""",

# 【動態執行程式碼】
# 高風險、難推理
"""
Avoid using `eval`, `exec`, or dynamic code execution unless there is a strong justification.
These constructs can introduce serious security risks and make code harder to reason about.
""",
]
