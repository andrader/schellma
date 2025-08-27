"""Core Pydantic models for schellma package.

This module contains the core Pydantic model definitions used throughout
the schellma package for type conversion demonstrations and testing.

## Example

```python
from schellma.models import NestedModel, Status
model = NestedModel(text="hello", number=42)
print(model.text)
# Output: hello
```
"""

from enum import Enum

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
