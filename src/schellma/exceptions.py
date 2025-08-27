"""Custom exceptions for scheLLMa package.

This module defines the exception hierarchy used throughout scheLLMa
for handling various error conditions during schema conversion.

All exceptions inherit from ScheLLMaError, which provides a common
base for catching any scheLLMa-related errors.

## Example

```python
from schellma.exceptions import InvalidSchemaError
try:
    # Some conversion operation
    pass
except InvalidSchemaError as e:
    print(f"Schema error: {e}")
```
"""


class ScheLLMaError(Exception):
    """Base exception for all scheLLMa errors.

    This is the root exception class for all scheLLMa-specific errors.
    Catching this exception will catch any error raised by scheLLMa.

    ## Example

    ```python
    try:
        # scheLLMa operations
        pass
    except ScheLLMaError as e:
        print(f"scheLLMa error: {e}")
    ```
    """

    pass


# Keep schellmaError as alias for backward compatibility
schellmaError = ScheLLMaError


class InvalidSchemaError(ScheLLMaError):
    """Raised when a JSON schema is invalid or malformed.

    This exception is raised when the input schema doesn't conform
    to expected JSON Schema format or contains invalid structures.

    ## Common causes

    - Empty or non-dictionary schema
    - Invalid `$defs` structure
    - Malformed property definitions
    - Non-BaseModel classes passed to conversion functions

    ## Example

    ```python
    from schellma import json_schema_to_llm
    try:
        json_schema_to_llm({})  # Empty schema
    except InvalidSchemaError as e:
        print(f"Invalid schema: {e}")
    ```
    """

    pass


class ConversionError(ScheLLMaError):
    """Raised when conversion from JSON schema to TypeScript fails.

    This exception is raised when the conversion process encounters
    an error that prevents successful type generation, such as
    invalid type definitions or unsupported schema constructs.

    ## Common causes

    - Invalid type definitions in schema
    - Malformed `anyOf`/`oneOf` constructs
    - Invalid property names or structures
    - Failed nested conversions

    ## Example

    ```python
    from schellma import json_schema_to_llm
    try:
        json_schema_to_llm({"properties": "invalid"})
    except ConversionError as e:
        print(f"Conversion failed: {e}")
    ```
    """

    pass


class CircularReferenceError(ScheLLMaError):
    """Raised when a circular reference is detected in the schema.

    This exception is raised when the schema contains circular
    references that would cause infinite recursion during conversion.

    Circular references occur when a type definition references
    itself either directly or through a chain of other definitions.

    ## Example

    ```python
    schema = {
        "type": "object",
        "properties": {"self": {"$ref": "#/$defs/Self"}},
        "$defs": {
            "Self": {
                "type": "object",
                "properties": {"nested": {"$ref": "#/$defs/Self"}}
            }
        }
    }
    try:
        json_schema_to_llm(schema, define_types=False)
    except CircularReferenceError as e:
        print(f"Circular reference: {e}")
    ```
    """

    pass


class UnsupportedTypeError(ScheLLMaError):
    """Raised when an unsupported type is encountered during conversion.

    This exception is raised when the converter encounters a type
    or schema construct that is not currently supported by scheLLMa.

    While scheLLMa supports most common JSON Schema constructs,
    some advanced or rarely-used features may not be implemented.

    ## Note

    Currently most types are supported, so this exception is rarely raised.
    It's included for future extensibility when new schema features are encountered.
    """

    pass
