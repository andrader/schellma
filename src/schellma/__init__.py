"""# scheLLMa - Schemas for LLMs

scheLLMa is a professional Python package that converts Pydantic models
to clean, simplified type definitions perfect for LLM prompts. Unlike verbose
JSON Schema formats, scheLLMa produces readable, concise schemas that are
ideal for language model interactions.

## Why scheLLMa?

When working with LLMs, you need clean, readable schemas that:
- **Reduce token usage** - Concise format saves on API costs
- **Improve LLM understanding** - Simple syntax is easier for models to parse
- **Minimize errors** - Less verbose than JSON Schema, reducing confusion
- **Stay readable** - Human-friendly format for prompt engineering

## Key Features

- Optimized for LLM prompts with clean, readable type definitions
- Support for all common Python types (str, int, bool, etc.)
- Handle complex nested structures and collections
- Support for enums, optional types, and unions
- Comprehensive error handling with descriptive messages
- Circular reference detection and prevention
- Customizable output formatting
- Token-efficient output reduces LLM API costs

## Basic Usage

```python
from pydantic import BaseModel
from schellma import pydantic_to_llm

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# Generate clean schema for LLM prompts
schema = pydantic_to_llm(User)
print(schema)
```

Output:
```typescript
{
    "name": string,
    "age": int,
    "email": string | null,
}
```

## LLM Integration

```python
from schellma import pydantic_to_llm

class TaskRequest(BaseModel):
    title: str
    priority: int
    tags: list[str]

schema = pydantic_to_llm(TaskRequest)

prompt = f'''
Please create a task with this structure:
{schema}
'''
# Use with OpenAI, Anthropic, or any LLM API
```

## Error Handling

```python
from schellma.exceptions import InvalidSchemaError, ConversionError
try:
    result = pydantic_to_llm(SomeModel)
except InvalidSchemaError as e:
    print(f"Schema validation failed: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```
"""

from . import exceptions
from .converters import json_schema_to_llm, pydantic_to_llm, to_llm

__version__ = "0.2.0"
__all__ = [
    "json_schema_to_llm",
    "pydantic_to_llm",
    "to_llm",
    "exceptions",
]


def main() -> None:
    """Main entry point for CLI.

    Prints a comprehensive test example showing all supported type conversions.
    """
    from .examples import ComprehensiveTest

    print("\n=== ComprehensiveTest - All supported types ===")
    result = pydantic_to_llm(ComprehensiveTest, define_types=True, indent=2)
    print(result)
