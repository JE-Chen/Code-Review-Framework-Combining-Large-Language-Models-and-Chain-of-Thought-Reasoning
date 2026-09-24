- Code Smell Type: Violation of Single Responsibility Principle (SRP) & Tight Coupling
- Problem Location: `ReportFormatter.format` and `ExportManager.create_exporter`
- Detailed Explanation: 
    1. `ReportFormatter` is directly accessing the global `CONFIG` object to decide whether to uppercase text. A formatter should be a pure utility that transforms data based on parameters passed to it, not based on global state.
    2. `ExportManager` is acting as both a coordinator and a Factory. It contains the hard-coded logic to instantiate specific exporter classes based on `CONFIG`. This makes it difficult to add new exporters without modifying the manager.
- Improvement Suggestions: 
    1. Pass the `uppercase` requirement as an argument to the `format` method.
    2. Extract the exporter creation logic into a separate `ExporterFactory` class.
- Priority Level: High

- Code Smell Type: Shared Mutable State (Global Configuration)
- Problem Location: `CONFIG` dictionary and its usage across `ReportFormatter`, `ExportManager`, and `main()`.
- Detailed Explanation: The application relies on a global `CONFIG` dictionary that is mutated at runtime in `main()`. This creates hidden coupling between unrelated classes and makes the code non-thread-safe and difficult to test in isolation, as the behavior of `ReportService` changes based on a global variable.
- Improvement Suggestions: Use a Configuration object or a Dependency Injection pattern. Pass the required settings into the constructors of the classes that need them.
- Priority Level: High

- Code Smell Type: Inefficient String Concatenation (Performance Pitfall)
- Problem Location: `ReportFormatter.format` and `ReportService.generate` (the `buffer` loop).
- Detailed Explanation: 
    1. In `ReportFormatter`, `text = text + r` inside a loop creates a new string object in every iteration (O(n²)).
    2. In `ReportService.generate`, the loop `for ch in prepared: buffer = buffer + ch` is redundant and highly inefficient, as it manually rebuilds a string character by character.
- Improvement Suggestions: 
    1. Use `''.join(list_of_strings)` for concatenating multiple strings.
    2. Remove the `buffer` loop entirely; `prepared` is already a string.
- Priority Level: Medium

- Code Smell Type: Refused Bequest / Interface Pollution
- Problem Location: `BaseExporter.finish()` and its overrides.
- Detailed Explanation: The `BaseExporter` defines a `finish()` method that is not used by the `ReportService` and is ignored by `JsonLikeExporter`. This forces subclasses to either implement a useless method or inherit a method that does nothing, indicating that the base abstraction is too broad or incorrectly defined.
- Improvement Suggestions: Remove `finish()` from the base class. If only some exporters need a cleanup phase, create a separate `DisposableExporter` interface.
- Priority Level: Low

- Code Smell Type: Unclear Naming / Variable Shadowing
- Problem Location: `ReportService.generate` -> `report = content`
- Detailed Explanation: The variable `report` is initially passed as a `Report` object (containing title and rows), but is then reassigned to a string (`content`). This changes the semantic meaning of the variable mid-function, which is confusing for maintainers and can lead to type-related bugs.
- Improvement Suggestions: Use a distinct name for the formatted string, such as `formatted_content`.
- Priority Level: Low