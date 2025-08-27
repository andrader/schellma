"""Constants for scheLLMa package.

This module contains all the constants used throughout scheLLMa
for consistent formatting and type conversion.

These constants centralize all magic numbers, hardcoded strings,
and template patterns used in the conversion process, making
the codebase more maintainable and allowing easy customization
of output formatting.

## Example

```python
from schellma.constants import TS_TYPE_MAPPINGS
print(TS_TYPE_MAPPINGS["string"])
# Output: string
```
"""

# JSON Schema reference patterns
DEFS_PREFIX = "#/$defs/"

# TypeScript type mappings
TS_TYPE_MAPPINGS = {
    "string": "string",
    "integer": "int",
    "number": "number",
    "boolean": "boolean",
}

# TypeScript template strings
TS_ARRAY_TEMPLATE = "{type}[]"
TS_TUPLE_TEMPLATE = "[{types}]"
TS_INDEX_SIGNATURE_TEMPLATE = "{{ [key: string]: {type} }}"
TS_INDEX_SIGNATURE_ANY = "{ [key: string]: any }"
TS_UNION_SEPARATOR = " | "
TS_NULL_TYPE = "null"
TS_ANY_TYPE = "any"
TS_OBJECT_TYPE = "object"
TS_ANY_ARRAY_TYPE = "any[]"

# Object formatting (will be dynamically generated based on indent parameter)
OBJECT_OPEN_BRACE = "{"
DEFINITION_SEPARATOR = "\n\n"
EMPTY_LINE = ""

# Default indentation
DEFAULT_INDENT = 2

# Enum formatting
ENUM_VALUE_TEMPLATE = '"{value}"'
