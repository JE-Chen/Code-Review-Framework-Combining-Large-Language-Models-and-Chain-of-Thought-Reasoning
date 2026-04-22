## Summary Rules
### Key Changes
- Added `StringProcessor` and `NumberProcessor` classes to process string and number data respectively.
- Created `DataPipeline` class to manage processing steps and execute them sequentially.
- Introduced `GLOBAL_CONFIG` dictionary for configuration settings.
- Refactored `main` function to use the `DataPipeline`.

### Impact Scope
- Affected modules: `BaseProcessor`, `StringProcessor`, `NumberProcessor`, `DataPipeline`.
- Files: All files containing the above classes and functions.

### Purpose of Changes
- To provide a flexible data processing pipeline system capable of handling different types of data (strings and numbers).
- To encapsulate configuration settings in a single location (`GLOBAL_CONFIG`).

### Risks and Considerations
- Potential impact on existing functionality: Existing code might need adjustments to utilize the new processing pipeline.
- Areas requiring extra testing: The new classes and their interactions need thorough testing to ensure they behave as expected.

### Items to Confirm
- Validate that the processing steps work correctly with various inputs.
- Ensure that the `GLOBAL_CONFIG` is used consistently throughout the application.
- Review the logic inside the nested conditional statements in the `main` function for correctness.

## Code Diff to Review
```python
class BaseProcessor:
    def process(self, data):
        return data

class StringProcessor(BaseProcessor):
    def process(self, data):
        if isinstance(data, str):
            result = ""
            for ch in data:
                if ch.isalpha():
                    result += ch.upper()
                else:
                    result += str(ord(ch))
            return result
        return super().process(data)

class NumberProcessor(BaseProcessor):
    def process(self, data):
        if isinstance(data, int):
            return (data * 1234) % 5678 + 9999
        return super().process(data)

class DataPipeline:
    def __init__(self):
        self.steps = []

    def add_step(self, processor):
        self.steps.append(processor)

    def run(self, data):
        result = data
        for step in self.steps:
            result = step.process(result)
        return result

GLOBAL_CONFIG = {
    "mode": "weird",
    "threshold": 123456,
    "flag": True
}

def main():
    pipeline = DataPipeline()
    pipeline.add_step(StringProcessor())
    pipeline.add_step(NumberProcessor())

    input_data = "abc123"
    output = pipeline.run(input_data)

    print("Input:", input_data)
    print("Output:", output)

    val = 7
    if GLOBAL_CONFIG["flag"]:
        if val > 5:
            if val < GLOBAL_CONFIG["threshold"]:
                if GLOBAL_CONFIG["mode"] == "weird":
                    print("Strange mode active:", val)
                else:
                    print("Normal mode:", val)
            else:
                print("Value too large")
        else:
            print("Value too small")
    else:
        print("Flag disabled")

if __name__ == "__main__":
    main()
```

This code introduces a flexible data processing pipeline system using inheritance and composition. It also demonstrates how configuration settings can be managed centrally. The `main` function showcases the usage of the pipeline with sample data.