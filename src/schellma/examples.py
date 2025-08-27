"""Example models demonstrating schellma functionality.

This module contains comprehensive example models that showcase
the full range of type conversions supported by schellma.

These models are primarily used for testing and demonstration
purposes, showing how different Python/Pydantic types are
converted to TypeScript-like type definitions.

## Example

```python
from schellma.examples import ComprehensiveTest
from schellma import pydantic_to_llm
ts_type = pydantic_to_llm(ComprehensiveTest)
print(ts_type)
```
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .models import NestedModel, Status


class ComprehensiveTest(BaseModel):
    """Comprehensive test model demonstrating all supported type conversions.

    This model includes examples of every type that schellma can convert
    from Pydantic models to TypeScript-like type definitions, including:

    - Basic primitive types (str, int, bool, etc.)
    - Date/time types (datetime, date, time)
    - UUID and Decimal types
    - Collection types (List, Set, Dict, Tuple)
    - Optional types and unions
    - Nested models and enums
    - Complex nested structures

    This model is primarily used for testing the conversion functionality
    and serves as a comprehensive example of supported types.

    ## Attributes

    - **text**: A simple text field
    - **number**: An integer field
    - **decimal_val**: A decimal number field
    - **is_active**: A boolean flag
    - **created_at**: A datetime timestamp
    - **birth_date**: A date field
    - **meeting_time**: A time field
    - **user_id**: A UUID identifier
    - **tags**: A list of string tags
    - **scores**: A set of integer scores
    - **metadata**: A dictionary with string keys and any values
    - **coordinates**: A tuple of two floats (x, y coordinates)
    - **variable_tuple**: A variable-length tuple of strings
    - **optional_text**: An optional text field
    - **optional_nested**: An optional nested model
    - **nested_dict**: A dictionary containing lists of nested models
    - **tuple_with_models**: A tuple containing exactly two nested models
    - **status**: An enum field representing status
    """

    # Basic types
    text: str = Field(description="A text field")
    number: int
    decimal_val: Decimal
    is_active: bool
    created_at: datetime
    birth_date: date
    meeting_time: time
    user_id: UUID

    # Collections
    tags: list[str]
    scores: set[int]
    metadata: dict[str, Any]
    coordinates: tuple[float, float]
    variable_tuple: tuple[str, ...]

    # Optional types
    optional_text: str | None
    optional_nested: NestedModel | None

    # Complex nested
    nested_dict: dict[str, list[NestedModel]]
    tuple_with_models: tuple[NestedModel, NestedModel]

    # Enum
    status: Status
