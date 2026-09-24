### Title
A Python program that processes data through multiple steps using a configurable pipeline.

### Overview
This program demonstrates a simple data processing pipeline where different types of processors can be added to handle various data transformations. The pipeline is configured using a global dictionary and executed with specific input data.

### Detailed Explanation
#### Step-by-Step Flow
1. **Class Definitions**:
   - `BaseProcessor`: A base class with a generic `process` method.
   - `StringProcessor`: Inherits from `BaseProcessor` and overrides the `process` method to convert alphabetic characters to uppercase and non-alphabetic characters to their ASCII values.
   - `NumberProcessor`: Inherits from `BaseProcessor` and overrides the `process` method to apply a mathematical transformation to integer data.

2. **DataPipeline Class**:
   - Manages a sequence of processors (`steps`).
   - Provides methods to add processors and run the pipeline on given data.

3. **Global Configuration**:
   - Contains configuration settings such as mode, threshold, and flag.

4. **Main Function**:
   - Initializes the data pipeline and adds string and number processors.
   - Runs the pipeline with sample input data.
   - Uses the global configuration to conditionally print messages based on certain conditions.

#### Inputs/Outputs
- **Inputs**: 
  - Global configuration dictionary.
  - Input data for the pipeline.
  
- **Outputs**:
  - Processed data after passing through all pipeline steps.
  - Conditional prints based on the global configuration.

#### Key Functions, Classes, or Modules
- `BaseProcessor`, `StringProcessor`, `NumberProcessor`: Processor classes.
- `DataPipeline`: Manages the pipeline execution.
- `GLOBAL_CONFIG`: Global configuration dictionary.

#### Assumptions, Edge Cases, and Possible Errors
- Assumes all processors correctly implement the `process` method.
- Edge case: Non-string and non-integer data passed to processors.
- Error handling not explicitly shown; may raise exceptions if data types mismatch.

#### Performance or Security Concerns
- Potential performance issue if many processors are chained together.
- Security risks if global configuration is directly modified or accessed without validation.

#### Suggested Improvements
1. **Error Handling**: Add try-except blocks to catch and log errors during pipeline execution.
2. **Type Checking**: Validate input data types before processing.
3. **Configuration Validation**: Ensure global configuration is validated before use.
4. **Logging**: Replace direct print statements with logging for better control over output.

### Example Usage
```python
# Sample usage of the DataPipeline with custom processors
pipeline = DataPipeline()
pipeline.add_step(StringProcessor())
pipeline.add_step(NumberProcessor())

input_data = "hello123"
output = pipeline.run(input_data)
print("Processed Output:", output)
```

This example demonstrates how to extend the pipeline with new processors and run them on custom input data.