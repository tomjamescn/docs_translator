# Basic Example

This example demonstrates the basic usage of the Sample Project.

```python
# Import the necessary modules
from sample_project import SampleClass
from sample_project.utils import format_data

# Create a sample instance
sample = SampleClass(param1="example", param2=42)

# Process some data
input_data = "Sample input data"
result = sample.process_data(input_data)

# Format the result
formatted_result = format_data(result)

print(f"Formatted result: {formatted_result}")
```

## Expected Output

```
Formatted result: {"status": "success", "data": "Processed: Sample input data"}
```
