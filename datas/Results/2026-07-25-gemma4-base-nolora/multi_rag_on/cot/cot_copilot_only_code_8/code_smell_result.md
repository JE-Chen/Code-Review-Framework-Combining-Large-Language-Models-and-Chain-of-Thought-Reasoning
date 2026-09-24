- Code Smell Type: Unclear Naming
- Problem Location: `self.btnA`, `self.btnB`, `self.labelX`, `self.textArea`
- Detailed Explanation: The variables use generic suffixes (A, B, X) rather than descriptive names. This forces a developer to read the implementation logic to understand the purpose of the widget. As the UI grows, names like `btnA` become meaningless and hinder maintainability.
- Improvement Suggestions: Rename variables to reflect their function. For example: `self.btn_calculate_length`, `self.btn_check_category`, `self.status_label`, and `self.input_text_area`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional (Arrow Anti-pattern)
- Problem Location: `handle_btnB` method
- Detailed Explanation: The method uses multiple levels of nested `if/else` statements to categorize text length. This increases cognitive load and makes the logic harder to follow and modify. It violates the principle of keeping code flat and readable.
- Improvement Suggestions: Use "Guard Clauses" to handle the empty case early, and then use a flat `if/elif/else` structure or a data-driven approach (e.g., a list of tuples containing thresholds and labels) to determine the text category.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `CustomWidget.__init__`
- Detailed Explanation: The constructor is handling two distinct responsibilities: defining the UI components/layout and defining the business logic (connecting signals to slots). In larger widgets, this leads to bloated constructors that are difficult to test or modify.
- Improvement Suggestions: Separate the UI setup into a dedicated method (e.g., `self.setup_ui()`) and the signal connections into another (e.g., `self.setup_connections()`).
- Priority Level: Low