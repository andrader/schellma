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
from schellma import pydantic_to_schellma

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# Generate clean schema for LLM prompts
schema = pydantic_to_schellma(User)
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
from schellma import pydantic_to_schellma

class TaskRequest(BaseModel):
    title: str
    priority: int
    tags: list[str]

schema = pydantic_to_schellma(TaskRequest)

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
    result = pydantic_to_schellma(SomeModel)
except InvalidSchemaError as e:
    print(f"Schema validation failed: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```
"""

from . import exceptions
from .converters import json_schema_to_schellma, pydantic_to_schellma, schellma

__version__ = "0.3.1"
__all__ = [
    "json_schema_to_schellma",
    "pydantic_to_schellma",
    "schellma",
    "exceptions",
]
