# scheLLMa

_Schemas for LLMs and Structured Output_

[![Documentation](https://img.shields.io/badge/Documentation-blue)](https://andrader.github.io/schellma/)
[![Demo and Examples](https://img.shields.io/badge/Demo_and_Examples-blue)](https://andrader.github.io/schellma/demo/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/schellma.svg)](https://badge.fury.io/py/schellma)
![PyPI - Downloads](https://img.shields.io/pypi/dm/schellma)



Converts Pydantic models/JSON Schemas to clean, simplified type definitions perfect for **generating structured output** with **LLM prompts**. 

Unlike verbose JSON Schema formats, **scheLLMa** produces readable, concise type definitions that are ideal for language model interactions and structured output generation:

- **Reduce token usage** - Concise format saves on API costs
- **Minimize parsing errors** - Simple syntax is easier for models to parse, less verbose than JSON Schema, reducing confusion
- **Stay readable** - Human-friendly format for prompt engineering

View the [documentation](https://andrader.github.io/schellma/) for more details.

Checkout the [demo](https://andrader.github.io/schellma/demo/) for more examples!

Combine it with parsing libs, like `openai` sdk or `Instructor` for AWESOME results!

- [scheLLMa](#schellma)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Using the new openai chat.completions.**parse** API](#using-the-new-openai-chatcompletionsparse-api)
    - [Using the new openai Responses API](#using-the-new-openai-responses-api)
  - [Installation](#installation)
    - [Comparison with JSON Schema](#comparison-with-json-schema)
  - [Advanced Usage with Type Definitions](#advanced-usage-with-type-definitions)
  - [Examples](#examples)
    - [Enum Support](#enum-support)
    - [Complex Nested Structures](#complex-nested-structures)
  - [Development](#development)
    - [Setup](#setup)
    - [Running Tests](#running-tests)
    - [Type Checking](#type-checking)
    - [Linting](#linting)
  - [Contributing](#contributing)
    - [Development Guidelines](#development-guidelines)
  - [License](#license)
  - [Changelog](#changelog)


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

View the [demo](demo.md) for more examples and features!

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

# Add the scheLLMa schema to the prompt
prompt = f"""
Please create a task with the following structure:

{schema}
"""
print(prompt)

# Use with your favorite LLM API
completion = openai.chat.completions.create(
    model="gpt-4.1-mini",
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

### Using the new openai chat.completions.**parse** API

```python
# or directly parse with openai sdk
completion = openai.chat.completions.parse(
    model="gpt-4.1-mini",
    messages=[{
        "role": "user",
        "content": prompt
    }]
)
task = completion.choices[0].message.parsed
print(task)
# TaskRequest(title='Task 1', priority=1, tags=['tag1', 'tag2'], due_date=None)
```

### Using the new openai Responses API

```python
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

schema = schellma(CalendarEvent)

response = openai.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        # Make sure to include the schema in your prompt
        {"role": "system", "content": f"Extract the event information. {schema}"},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    text_format=CalendarEvent,
)

event = response.output_parsed
print(event)
# CalendarEvent(name='Alice and Bob are going to a science fair on Friday.', date='Friday', participants=['Alice', 'Bob'])
```



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




## Examples

View more exemples at [Demo](#demo.md)

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
