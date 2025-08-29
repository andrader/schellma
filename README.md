# scheLLMa

_Schemas for LLMs and Structured Output_

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/schellma.svg)](https://badge.fury.io/py/schellma)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Converts Pydantic models/JSON Schemas to clean, simplified type definitions perfect for **generating structured output** with **LLM prompts**. 

Unlike verbose JSON Schema formats, **scheLLMa** produces readable, concise type definitions that are ideal for language model interactions and structured output generation:

- **Reduce token usage** - Concise format saves on API costs
- **Minimize parsing errors** - Simple syntax is easier for models to parse, less verbose than JSON Schema, reducing confusion
- **Stay readable** - Human-friendly format for prompt engineering

<div class="grid" markdown>


!!! note ""
    === "Pydantic"


        ```python
        from pydantic import BaseModel, Field
        from schellma import schellma

        class User(BaseModel):
            name: str = Field(default="Anonymous", description="The name of the user")
            age: int = Field(ge=0, le=150, description="User age in years")
            email: str | None = Field(None, examples=["user@example.com"])
        ```

    === "JSON Schema"

        ```json
        {
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "The name of the user" },
            "age": { "type": "integer" },
            "email": { "type": ["string", "null"], "default": null }
        },
        "required": ["name", "age"],
        "additionalProperties": false
        }
        ```


!!! tip "ScheLLMa"



    ```typescript
    {
        // The name of the user, default: "Anonymous", optional
        "name": string,
        // User age in years, range: 0-150, required
        "age": int,
        // default: null, example: "user@example.com", optional
        "email": string | null,
    }
    ```


    



</div>





## Features

- 🤖 **Optimized for LLM prompts** - Clean, readable type definitions
- 💰 **Token-efficient** - Reduces LLM API costs
- 🎯 **Support for all common Python types** (str, int, bool, datetime, etc.)
- 🏗️ **Handle complex nested structures and collections** - Strong support for Pydantic model types
- 🔗 **Support for enums, optional types, and unions** - Properly extract and display union types
- ⚙️ **Customizable output formatting** - Indentation, compact mode, and more
- 🎨 **Rich Default Values** - Automatically shows default values in human-readable comments
- 📏 **Smart Constraints** - Displays field constraints (length, range, patterns) in clear language
- ✅ **Clear Field Status** - Explicit required/optional marking
- 📚 **Rich Examples** - Inline examples and documentation for better LLM understanding
- 🔀 **Advanced Union Types** - Full support for allOf, not constraints, and discriminated unions
- 🔢 **Advanced Arrays** - Contains constraints, minContains/maxContains, and enhanced tuple support


## Quick Start



```python
from pydantic import BaseModel
from schellma import schellma

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# Convert to clean schema for LLM prompts
schema = schellma(User)
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

View the [demo](demo.md) for more examples.

## Installation

```bash
pip install schellma
```

Or using uv:

```bash
uv add schellma
```

Install from github

```bash
uv add git+https://github.com/andrader/schellma.git
```


## LLM Prompt Integration

```python
from pydantic import BaseModel
from schellma import schellma
import openai

class TaskRequest(BaseModel):
    title: str
    priority: int
    tags: list[str]
    due_date: str | None = None

# Generate schema for LLM prompt
schema = schellma(TaskRequest)


prompt = f"""
Please create a task with the following structure:

{schema}
"""
print(prompt)

# Use with your favorite LLM API
completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": prompt
    }]
)

content = completion.choices[0].message.content
print(content)



task = TaskRequest.model_validate_json(clean_content(content))
print(task)
# TaskRequest(title='Task 1', priority=1, tags=['tag1', 'tag2'], due_date=None)
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
from schellma import schellma

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
schema = schellma(User, define_types=True)
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

schema = schellma(Task)
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

schema = schellma(Post, define_types=True)
```

### Indentation Control

```python
from schellma import schellma

class User(BaseModel):
    name: str
    age: int

# Default indentation (2 spaces)
result = schellma(User)
# Output:
# {
#   "name": string,
#   "age": int,
# }

# Custom indentation (4 spaces)
result = schellma(User, indent=4)
# Output:
# {
#     "name": string,
#     "age": int,
# }

# No indentation (compact for minimal tokens)
result = schellma(User, indent=False)
# Output: {"name": string,"age": int,}
```



## LLM Integration Examples

### OpenAI Integration

```python
import openai
from pydantic import BaseModel
from schellma import schellma

class Response(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

schema = schellma(Response)

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
from schellma import schellma

schema = schellma(MyModel, indent=False)  # Compact for tokens

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

See [Changelog](CHANGELOG.md) for the changelog.
