# Advanced Example

This example demonstrates advanced usage of the Sample Project, including custom options and report generation.

```python
# Import the necessary modules
from sample_project import SampleClass
from sample_project.utils import format_data, validate_input

# Validate user input
user_input = "Advanced sample data"
if not validate_input(user_input):
    print("Invalid input")
    exit(1)

# Create a sample instance with custom parameters
sample = SampleClass(param1="advanced_example", param2=100)

# Define custom processing options
options = {
    "transform": "uppercase",
    "filter": ["noise", "redundancy"],
    "max_length": 200
}

# Process the data with custom options
result = sample.process_data(user_input, options=options)

# Generate different report formats
json_report = sample.generate_report(format="json")
xml_report = sample.generate_report(format="xml")
csv_report = sample.generate_report(format="csv")

print("JSON Report:")
print(json_report)
print("\nXML Report:")
print(xml_report)
print("\nCSV Report:")
print(csv_report)
```

## Expected Output

```
JSON Report:
{"status": "success", "data": "ADVANCED SAMPLE DATA", "options": {"transform": "uppercase", "filter": ["noise", "redundancy"], "max_length": 200}}

XML Report:
<result>
  <status>success</status>
  <data>ADVANCED SAMPLE DATA</data>
  <options>
    <transform>uppercase</transform>
    <filter>noise,redundancy</filter>
    <max_length>200</max_length>
  </options>
</result>

CSV Report:
status,data,transform,filter,max_length
success,ADVANCED SAMPLE DATA,uppercase,"noise,redundancy",200
```
