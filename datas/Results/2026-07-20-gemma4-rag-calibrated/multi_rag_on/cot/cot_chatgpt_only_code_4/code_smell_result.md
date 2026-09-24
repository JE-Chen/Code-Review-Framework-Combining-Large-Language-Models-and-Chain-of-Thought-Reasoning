- Code Smell Type: Violation of Single Responsibility Principle (SRP) & Tight Coupling
- Problem Location: `ReportFormatter.format` and `ReportService.generate`
- Detailed Explanation: The `ReportFormatter` is directly accessing the global `CONFIG` object to decide whether to uppercase text. This couples the formatting logic to a global configuration state. Furthermore, `ReportService.generate` handles formatting, preparation, and execution flow. The logic for "uppercasing" is duplicated across `ReportFormatter` and `UpperTextExporter`, creating confusion about where the transformation should actually occur.
- Improvement Suggestions: Pass the required configuration (e.g., `uppercase=True`) as an argument to the `format` method or the `ReportFormatter` constructor. Remove the transformation logic from the formatter if the `Exporter` is already intended to handle it.
- Priority Level: High

- Code Smell Type: Shared Mutable State (Global Configuration)
- Problem Location: `CONFIG` dictionary and its usage in `ReportFormatter` and `ExportManager`
- Detailed Explanation: The application relies on a global `CONFIG` dictionary that is mutated at runtime in `main()`. This makes the code difficult to test in parallel, creates hidden dependencies, and can lead to unpredictable behavior as the application grows. It violates the RAG rule regarding shared mutable state at the module level.
- Improvement Suggestions: Encapsulate configuration into a `Config` class or a data object and inject it into the classes that need it (Dependency Injection).
- Priority Level: High

- Code Smell Type: Inefficient String Concatenation in Loops
- Problem Location: `ReportFormatter.format` (`text = text + r + "\n"`) and `ReportService.generate` (`buffer = buffer + ch`)
- Detailed Explanation: In Python, strings are immutable. Using `+` in a loop creates a new string object in every iteration, leading to $O(n^2)$ time complexity. The loop in `ReportService.generate` is particularly egregious as it iterates over every single character of the prepared content just to rebuild the same string.
- Improvement Suggestions: Use `"".join(list_of_strings)` for concatenating sequences of strings. Remove the character-by-character loop in `ReportService.generate` entirely as it performs no meaningful transformation.
- Priority Level: Medium

- Code Smell Type: Refused Bequest / Interface Pollution
- Problem Location: `BaseExporter.finish()` and its overrides
- Detailed Explanation: The `BaseExporter` defines a `finish()` method that is not used by the `ReportService` and is ignored by `JsonLikeExporter`. This forces subclasses to either implement a useless method or inherit a method that does nothing, indicating that the base abstraction is not accurately representing the required behavior.
- Improvement Suggestions: Remove `finish()` from the base class. If only some exporters need a cleanup phase, introduce a separate `Disposable` or `Finalizable` interface.
- Priority Level: Low

- Code Smell Type: Time-Dependent Logic without Abstraction
- Problem Location: `ExportManager.run` (`time.time()`)
- Detailed Explanation: The code calls `time.time()` directly to calculate duration. This makes unit testing difficult because the results depend on the system clock and cannot be easily mocked or made deterministic. This violates the RAG rule regarding environment-dependent logic.
- Improvement Suggestions: Wrap time retrieval in a provider class or pass a clock function as a dependency to `ExportManager`.
- Priority Level: Low