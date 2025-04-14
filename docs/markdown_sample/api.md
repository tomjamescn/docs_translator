# API Reference

This document provides the API reference for the Sample Project.

## SampleClass

The main class for the Sample Project.

### Constructor

```python
SampleClass(param1="default", param2=0)
```

#### Parameters:

- `param1` (str): Description of param1
- `param2` (int): Description of param2

### Methods

#### process_data

```python
SampleClass.process_data(data, options=None)
```

Process the provided data.

##### Parameters:

- `data` (str): The data to process
- `options` (dict, optional): Processing options

##### Returns:

- `dict`: The processed data

##### Raises:

- `ValueError`: If the data is invalid

#### generate_report

```python
SampleClass.generate_report(format="json")
```

Generate a report in the specified format.

##### Parameters:

- `format` (str): The report format ("json", "xml", "csv")

##### Returns:

- `str`: The generated report

## Utility Functions

### format_data

```python
format_data(data, style="standard")
```

Format the provided data according to the specified style.

#### Parameters:

- `data` (dict): The data to format
- `style` (str): The formatting style

#### Returns:

- `str`: The formatted data

### validate_input

```python
validate_input(input_str)
```

Validate the provided input string.

#### Parameters:

- `input_str` (str): The input to validate

#### Returns:

- `bool`: True if valid, False otherwise
