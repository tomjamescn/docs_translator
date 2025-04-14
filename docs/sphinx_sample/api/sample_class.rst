Sample Class
===========

.. autoclass:: sample_project.SampleClass
   :members:
   :undoc-members:
   :show-inheritance:

Example
-------

Here's an example of how to use the SampleClass:

.. code-block:: python

    from sample_project import SampleClass
    
    # Create an instance with default parameters
    sample = SampleClass()
    
    # Or with custom parameters
    custom_sample = SampleClass(param1="value1", param2=42)
    
    # Process some data
    result = custom_sample.process_data("example data")
