Utilities
=========

.. automodule:: sample_project.utils
   :members:
   :undoc-members:
   :show-inheritance:

Common Functions
---------------

.. code-block:: python

    from sample_project.utils import format_data, validate_input
    
    # Format some data
    formatted = format_data({"key": "value"})
    
    # Validate user input
    is_valid = validate_input("user_input")
    if is_valid:
        print("Input is valid!")
    else:
        print("Invalid input")
