# scheLLMa

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/schellma.svg)](https://badge.fury.io/py/schellma)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**scheLLMa** - _Schemas for LLMs_

A professional Python package that converts Pydantic models to clean, simplified type definitions perfect for LLM prompts. Unlike verbose JSON Schema formats (used by tools like Instructor), scheLLMa produces readable, concise type definitions that are ideal for language model interactions.

## Why scheLLMa?

When working with LLMs, you need clean, readable schemas that:

- **Reduce token usage** - Concise format saves on API costs
- **Improve LLM understanding** - Simple syntax is easier for models to parse
- **Minimize errors** - Less verbose than JSON Schema, reducing confusion
- **Stay readable** - Human-friendly format for prompt engineering

## Features

- 🤖 **Optimized for LLM prompts** - Clean, readable type definitions
- 🎯 **Support for all common Python types** (str, int, bool, datetime, etc.)
- 🏗️ **Handle complex nested structures and collections**
- 🔗 **Support for enums, optional types, and unions**
- 🛡️ **Comprehensive error handling** with descriptive messages
- 🔍 **Circular reference detection** and prevention
- ⚙️ **Customizable output formatting**
- 📝 **Full type safety** with mypy support
- 💰 **Token-efficient** - Reduces LLM API costs

## Installation

```bash
pip install schellma
```

Or using uv:

```bash
uv add schellma
```

## Quick Start

### Basic Usage

```python
from pydantic import BaseModel
from schellma import pydantic_to_typescript_type

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# Convert to clean schema for LLM prompts
schema = pydantic_to_typescript_type(User)
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

### LLM Prompt Integration

```python
from pydantic import BaseModel
from schellma import pydantic_to_typescript_type

class TaskRequest(BaseModel):
    title: str
    priority: int
    tags: list[str]
    due_date: str | None = None

# Generate schema for LLM prompt
schema = pydantic_to_typescript_type(TaskRequest)

prompt = f"""
Please create a task with the following structure:

{schema}

Make sure to include a title and priority level.
"""

# Use with your favorite LLM API
# response = openai.chat.completions.create(...)
```

### Comparison with JSON Schema

**JSON Schema (verbose, token-heavy):**

```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "age": { "type": "integer" },
    "email": { "type": ["string", "null"], "default": null }
  },
  "required": ["name", "age"],
  "additionalProperties": false
}
```

**scheLLMa (clean, token-efficient):**

```typescript
{
    "name": string,
    "age": int,
    "email": string | null,
}
```

## Advanced Usage with Type Definitions

```python
from pydantic import BaseModel
from typing import List, Optional
from schellma import pydantic_to_typescript_type

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    age: int
    addresses: List[Address]
    primary_address: Optional[Address] = None

# Generate with separate type definitions
schema = pydantic_to_typescript_type(User, define_types=True)
print(schema)
```

Output:

```typescript
Address {
    "street": string,
    "city": string,
    "country": string,
}

{
    "name": string,
    "age": int,
    "addresses": Address[],
    "primary_address": Address | null,
}
```

## Supported Types

scheLLMa supports a comprehensive range of Python and Pydantic types:

### Basic Types

- `str` → `string`
- `int` → `int`
- `float` → `number`
- `bool` → `boolean`

### Date/Time Types

- `datetime` → `string`
- `date` → `string`
- `time` → `string`

### Collection Types

- `List[T]` → `T[]`
- `Set[T]` → `T[]`
- `Dict[str, T]` → `{ [key: string]: T }`
- `Tuple[T, U]` → `[T, U]`
- `Tuple[T, ...]` → `T[]`

### Optional and Union Types

- `Optional[T]` → `T | null`
- `Union[T, U]` → `T | U`
- `T | None` → `T | null`

### Complex Types

- **Enums** → Union of string literals
- **Nested Models** → Object types or references
- **UUID** → `string`
- **Decimal** → `number`

## API Reference

### `pydantic_to_typescript_type(model_class, define_types=False, indent=2)`

Convert a Pydantic model to clean schema for LLM prompts.

**Parameters:**

- `model_class` (Type[BaseModel]): The Pydantic model class to convert
- `define_types` (bool): If True, define reused types separately to avoid repetition
- `indent` (Union[int, bool, None]): Indentation configuration:
  - `False`/`None`/`0`: No indentation (compact format)
  - `int`: Number of spaces per indentation level (default: 2)

**Returns:**

- `str`: Clean schema definition for LLM prompts

**Raises:**

- `InvalidSchemaError`: If the model is invalid
- `ConversionError`: If conversion fails
- `CircularReferenceError`: If circular references are detected

### `json_schema_to_typescript(schema, define_types=True, indent=2)`

Convert a JSON Schema to clean schema for LLM prompts.

**Parameters:**

- `schema` (dict): JSON Schema dictionary
- `define_types` (bool): If True, define reused types separately
- `indent` (Union[int, bool, None]): Indentation configuration:
  - `False`/`None`/`0`: No indentation (compact format)
  - `int`: Number of spaces per indentation level (default: 2)

**Returns:**

- `str`: Clean schema definition for LLM prompts

## Error Handling

scheLLMa provides comprehensive error handling with descriptive messages:

```python
from schellma import pydantic_to_typescript_type
from schellma.exceptions import InvalidSchemaError, ConversionError

try:
    result = pydantic_to_typescript_type(MyModel)
except InvalidSchemaError as e:
    print(f"Schema validation failed: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```

### Exception Types

- **`ScheLLMaError`**: Base exception for all scheLLMa errors
- **`InvalidSchemaError`**: Raised when schema is invalid or malformed
- **`ConversionError`**: Raised when conversion fails
- **`CircularReferenceError`**: Raised when circular references are detected
- **`UnsupportedTypeError`**: Raised for unsupported types

## Examples

### Enum Support

```python
from enum import Enum
from pydantic import BaseModel

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Task(BaseModel):
    title: str
    status: Status

schema = pydantic_to_typescript_type(Task)
# Output: { "title": string, "status": "active" | "inactive" }
```

### Complex Nested Structures

```python
from pydantic import BaseModel
from typing import Dict, List

class Tag(BaseModel):
    name: str
    color: str

class Post(BaseModel):
    title: str
    content: str
    tags: List[Tag]
    metadata: Dict[str, str]

schema = pydantic_to_typescript_type(Post, define_types=True)
```

### Indentation Control

```python
from schellma import pydantic_to_typescript_type

class User(BaseModel):
    name: str
    age: int

# Default indentation (2 spaces)
result = pydantic_to_typescript_type(User)
# Output:
# {
#   "name": string,
#   "age": int,
# }

# Custom indentation (4 spaces)
result = pydantic_to_typescript_type(User, indent=4)
# Output:
# {
#     "name": string,
#     "age": int,
# }

# No indentation (compact for minimal tokens)
result = pydantic_to_typescript_type(User, indent=False)
# Output: {"name": string,"age": int,}
```

### CLI Usage

scheLLMa includes a simple CLI for quick testing:

```bash
python -m schellma
```

This will show a comprehensive example of all supported types.

## LLM Integration Examples

### OpenAI Integration

```python
import openai
from pydantic import BaseModel
from schellma import pydantic_to_typescript_type

class Response(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

schema = pydantic_to_typescript_type(Response)

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"Please respond with this structure: {schema}"
    }]
)
```

### Anthropic Claude Integration

```python
import anthropic
from schellma import pydantic_to_typescript_type

schema = pydantic_to_typescript_type(MyModel, indent=False)  # Compact for tokens

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{
        "role": "user",
        "content": f"Format your response as: {schema}"
    }]
)
```

## Development

### Setup

```bash
git clone https://github.com/andrader/schellma.git
cd schellma
uv sync --dev
```

### Running Tests

```bash
uv run python -m pytest
```

### Type Checking

```bash
uv run mypy src/schellma/
```

### Linting

```bash
uv run ruff check src/schellma/
uv run ruff format src/schellma/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow the existing code style (enforced by ruff)
2. Add tests for any new functionality
3. Update documentation as needed
4. Ensure all tests pass and type checking succeeds

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0

- Initial release as scheLLMa
- Optimized for LLM prompt integration
- Clean, token-efficient schema generation
- Support for all basic Python types
- Comprehensive error handling
- Circular reference detection
- Full test coverage
- Type safety with mypy
