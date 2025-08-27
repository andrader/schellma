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
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Status(Enum):
    """Status enumeration for various states.

    This enum represents different status values that can be used
    in models to indicate the current state of an entity.

    Attributes:
        ACTIVE: Entity is currently active and operational
        INACTIVE: Entity is inactive but can be reactivated
        PENDING: Entity is waiting for some action or approval
        COMPLETED: Entity has finished its lifecycle
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class NestedModel(BaseModel):
    """A simple nested model for testing and demonstration purposes.

    This model demonstrates basic field types and is used throughout
    the test suite to verify conversion functionality.

    Attributes:
        text (str): A string field with description
        number (int): An integer field with description

    Example:
        >>> model = NestedModel(text="example", number=123)
        >>> print(f"{model.text}: {model.number}")
        example: 123
    """

    text: str = Field(description="A text field")
    number: int = Field(description="A number field")


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

    Attributes:
        text (str): A simple text field
        number (int): An integer field
        decimal_val (Decimal): A decimal number field
        is_active (bool): A boolean flag
        created_at (datetime): A datetime timestamp
        birth_date (date): A date field
        meeting_time (time): A time field
        user_id (UUID): A UUID identifier
        tags (list[str]): A list of string tags
        scores (set[int]): A set of integer scores
        metadata (dict[str, Any]): A dictionary with string keys and any values
        coordinates (tuple[float, float]): A tuple of two floats (x, y coordinates)
        variable_tuple (tuple[str, ...]): A variable-length tuple of strings
        optional_text (str | None): An optional text field
        optional_nested (NestedModel | None): An optional nested model
        nested_dict (dict[str, list[NestedModel]]): A dictionary containing lists of nested models
        tuple_with_models (tuple[NestedModel, NestedModel]): A tuple containing exactly two nested models
        status (Status): An enum field representing status
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
