# this file contains funcitons that can extract information from our dsl (such as features of a function)

import inspect
import importlib
from typing import get_type_hints

# from . import dsl as module
from .dsl import Transformer

def get_dsl_functions():

    # Initialize the result dictionary
    function_info = {}

    # Iterate over all functions in the module
    for name, func in inspect.getmembers(Transformer, inspect.isfunction):

        # ignore the '__init__' function
        if not name == '__init__':

            # Get the function's signature
            signature = inspect.signature(func)
            # Get type hints for the function
            type_hints = get_type_hints(func)

            # Extract input types and output type
            input_types = list({
                param: type_hints.get(param, "Any")  # Default to "Any" if no type hint is provided
                for param in signature.parameters
            }.keys())
            output_type = type_hints.get("return", "Any")

            # Store the function's information
            function_info[name] = {
                "inputs": input_types,
                "output": output_type,
            }

    return function_info