#!/usr/bin/env python3
"""
Features Demonstration



Perfect for understanding scheLLMa's full capabilities for LLM integration.
"""

import inspect
import json
from textwrap import indent
from typing import Annotated, Any, Literal

import tiktoken
from pydantic import BaseModel, Field

from schellma.converters import schellma
from schellma.logger import get_logger, setup_logging

logger = get_logger()
setup_logging()


def code_block(language: str, code: str) -> str:
    return f"""```{language}\n{code}\n```"""


def admontion_block(title: str, content: str, type: str = "note") -> str:
    return f"""!!! {type} "{title}"
{indent(content, "    ")}
"""


def tab_block(title: str, content: str) -> str:
    return f"""=== "{title}"
{indent(content, "    ")}
"""


def grid_block(*args: str) -> str:
    args_str = "\n\n".join(args)
    return f"""<div class="grid" markdown>

{args_str}

</div>
"""


def count_tokens(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def demonstrate_feature(title: str, model_or_schema: Any, description: str) -> str:
    """Demonstrate a specific feature with clear output."""
    logger.info(f"Creating demo for '{title}'")

    if isinstance(model_or_schema, type) and issubclass(model_or_schema, BaseModel):
        py_code = inspect.getsource(model_or_schema)
        json_code = json.dumps(
            model_or_schema.model_json_schema(), indent=2, ensure_ascii=False
        )
    else:
        py_code = None
        json_code = json.dumps(model_or_schema, indent=2, ensure_ascii=False)

    schellma_code = schellma(model_or_schema, define_types=True)

    schellma_tokens = count_tokens(schellma_code)
    json_tokens = count_tokens(json_code)

    if py_code:
        demo_md = grid_block(
            admontion_block("Pydantic", code_block("python", py_code)),
            admontion_block(
                "ScheLLMa vs JSON Schema",
                tab_block(
                    f"ScheLLMa ({schellma_tokens} tokens)",
                    code_block("typescript", schellma_code),
                )
                + tab_block(
                    f"JSON Schema ({json_tokens} tokens)",
                    code_block("json", json_code),
                ),
            ),
        )
    else:
        demo_md = grid_block(
            admontion_block(
                f"JSON Schema ({json_tokens} tokens)",
                code_block("json", json_code),
            ),
            admontion_block(
                f"ScheLLMa ({schellma_tokens} tokens)",
                code_block("typescript", schellma_code),
                type="tip",
            ),
        )

    md = f"""## {title}\n\n{description}\n\n{demo_md}"""

    return md


# === 1. DEFAULT VALUES SUPPORT ===
class UserProfile(BaseModel):
    """User profile with comprehensive default values."""

    name: str = Field(default="Anonymous", description="User display name")
    age: Annotated[int, Field(ge=0)] = Field(default=0, description="User age in years")
    active: bool = Field(default=True, description="Account status")
    tags: list[str] = Field(default_factory=list, description="User tags")
    settings: dict[str, str] = Field(
        default_factory=lambda: {"theme": "dark", "lang": "en"},
        description="User preferences",
    )


# === 2. FIELD CONSTRAINTS ===
class ProductModel(BaseModel):
    """Product with comprehensive field constraints."""

    # String constraints
    name: str = Field(min_length=3, max_length=100, description="Product name")
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$", description="Product SKU")
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Contact email")

    # Numeric constraints
    price: float = Field(ge=0.01, le=999999.99, description="Product price")
    quantity: int = Field(ge=1, description="Stock quantity")
    discount: float = Field(multiple_of=0.05, description="Discount percentage")

    # Array constraints
    categories: list[str] = Field(
        min_length=1, max_length=5, description="Product categories"
    )
    tags: set[str] = Field(description="Unique product tags")


# === 3. ADVANCED UNION TYPES ===


# Discriminated Union
class User(BaseModel):
    type: Literal["user"] = "user"
    name: str
    email: str


class Admin(BaseModel):
    type: Literal["admin"] = "admin"
    name: str
    permissions: list[str]


class UserOrAdmin(BaseModel):
    entity: User | Admin = Field(discriminator="type")


# allOf-like inheritance
class BaseEntity(BaseModel):
    id: str = Field(description="Unique identifier")
    created_at: str = Field(description="Creation timestamp")


class ExtendedUser(BaseEntity):
    name: str = Field(description="User name")
    email: str = Field(description="User email")


# === 4. REQUIRED VS OPTIONAL FIELDS ===
class RegistrationForm(BaseModel):
    """Registration form with clear required/optional distinction."""

    # Required fields
    username: str = Field(description="Username for login")
    email: str = Field(description="Email address")
    password: str = Field(min_length=8, description="Account password")

    # Optional fields
    full_name: str | None = Field(None, description="Full display name")
    age: int | None = Field(None, ge=13, le=120, description="User age")
    bio: str | None = Field(None, max_length=500, description="User biography")


# === 5. EXAMPLES AND DOCUMENTATION ===
class APIRequest(BaseModel):
    """API request with rich examples."""

    method: str = Field(
        examples=["GET", "POST", "PUT", "DELETE"], description="HTTP method"
    )
    url: str = Field(
        examples=[
            "https://api.example.com/users",
            "https://api.example.com/products/123",
        ],
        description="Request URL",
    )
    headers: dict[str, str] | None = Field(
        None,
        examples=[
            {"Authorization": "Bearer token123", "Content-Type": "application/json"}
        ],
        description="Request headers",
    )
    body: dict | None = Field(
        None,
        examples=[{"name": "John Doe", "email": "john@example.com"}],
        description="Request body",
    )


# === 6. ADVANCED ARRAY TYPES ===

# Test advanced array schemas directly
advanced_array_schemas = {
    "contains_constraint": {
        "type": "object",
        "properties": {
            "required_tags": {
                "type": "array",
                "items": {"type": "string"},
                "contains": {"type": "string", "pattern": "^required_"},
                "minContains": 1,
                "maxContains": 3,
                "description": "Array must contain 1-3 items starting with 'required_'",
            }
        },
    },
    "advanced_tuple": {
        "type": "object",
        "properties": {
            "coordinates": {
                "type": "array",
                "prefixItems": [
                    {"type": "number", "description": "latitude"},
                    {"type": "number", "description": "longitude"},
                ],
                "items": {"type": "number"},
                "minItems": 2,
                "maxItems": 4,
                "description": "Coordinates with optional elevation and accuracy",
            }
        },
    },
    "not_constraint": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "not": {"enum": ["forbidden", "banned", "deleted"]},
                "description": "Any status except forbidden values",
            }
        },
    },
    "allof_intersection": {
        "type": "object",
        "allOf": [
            {
                "type": "object",
                "description": "Base fields",
                "properties": {
                    "id": {"type": "string", "description": "Unique ID"},
                    "created": {"type": "string", "description": "Creation time"},
                },
                "required": ["id", "created"],
            },
            {
                "type": "object",
                "description": "User fields",
                "properties": {
                    "name": {"type": "string", "description": "User name"},
                    "email": {"type": "string", "description": "User email"},
                },
                "required": ["name", "email"],
            },
        ],
    },
}


class ComprehensiveUserModel(BaseModel):
    """A comprehensive model showcasing all implemented features."""

    # Required fields with constraints and examples
    username: str = Field(
        description="Unique username for the account",
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["john_doe", "jane_smith", "user123"],
    )

    email: str = Field(
        description="User's email address",
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        examples=["john@example.com", "jane@company.org"],
    )

    # Optional fields with defaults, constraints, and examples
    name: str = Field(
        default="Anonymous User",
        description="Display name for the user",
        min_length=1,
        max_length=100,
        examples=["John Doe", "Jane Smith"],
    )

    age: int = Field(
        default=18,
        description="User's age in years",
        ge=13,
        le=120,
        examples=[25, 30, 35],
    )

    # Nullable fields with constraints and examples
    bio: str | None = Field(
        default=None,
        description="User's biography",
        max_length=500,
        examples=[
            "Software developer passionate about AI",
            "Love hiking and photography",
        ],
    )

    phone: str | None = Field(
        default=None,
        description="User's phone number",
        pattern=r"^\+?1?\d{9,15}$",
        examples=["+1-555-123-4567", "+44-20-7946-0958"],
    )

    # Array fields with constraints and examples
    tags: list[str] = Field(
        default_factory=list,
        description="User interest tags",
        min_length=0,
        max_length=10,
        examples=[["python", "ai", "music"], ["travel", "photography"]],
    )

    # Numeric fields with special constraints
    score: float = Field(
        default=0.0,
        description="User's reputation score",
        ge=0.0,
        le=100.0,
        examples=[85.5, 92.3, 78.1],
    )

    rating: int = Field(
        default=5,
        description="User's star rating",
        ge=1,
        le=5,
        multiple_of=1,
        examples=[4, 5],
    )

    # Complex default values
    preferences: dict[str, str] = Field(
        default={"theme": "dark", "language": "en", "timezone": "UTC"},
        description="User preferences and settings",
        examples=[
            {"theme": "light", "language": "es"},
            {"theme": "dark", "language": "fr"},
        ],
    )


def main() -> None:
    logger.info("Demonstrating features")
    texts = [
        "# **scheLLMa**: Features Demonstration",
        "This demonstrates some of the implemented features:",
        """## Key Features

- Default values shown in human-readable format
- String constraints (length, patterns) with smart formatting
- Numeric constraints (ranges, multiples) with clear descriptions
- Array constraints (item counts) with readable limits
- Required/optional field marking for clear API contracts
- Examples for better LLM understanding and human documentation
- Nullable type constraints properly extracted from union types
- Complex default values (objects, arrays) properly formatted


## Perfect for LLM Integration:
- Concise, readable format reduces token usage
- Rich context helps LLMs understand field requirements
- Examples provide clear guidance for data generation
- Constraints prevent invalid data creation
- Human-readable comments improve prompt engineering
""",
        # Feature 1: Default Values
        demonstrate_feature(
            "Default Values Support",
            UserProfile,
            "Shows default values in human-readable comments for better LLM understanding",
        ),
        # Feature 2: Field Constraints
        demonstrate_feature(
            "Field Constraints with Human-Readable Comments",
            ProductModel,
            "Displays string, numeric, and array constraints in clear, readable format",
        ),
        # Feature 3: Advanced Union Types - Discriminated Union
        demonstrate_feature(
            "Discriminated Union Types",
            UserOrAdmin,
            "Shows discriminated unions with clear type indicators",
        ),
        # Feature 3: Advanced Union Types - Inheritance (allOf-like)
        demonstrate_feature(
            "Inheritance (allOf-like behavior)",
            ExtendedUser,
            "Demonstrates inheritance patterns that work like allOf intersections",
        ),
        # Feature 3: Advanced Union Types - Direct allOf
        demonstrate_feature(
            "allOf Intersection Types",
            advanced_array_schemas["allof_intersection"],
            "Direct allOf schema merging with intersection comments",
        ),
        # Feature 3: Advanced Union Types - not constraints
        demonstrate_feature(
            "NOT Constraints",
            advanced_array_schemas["not_constraint"],
            "Exclusion constraints with human-readable descriptions",
        ),
        # Feature 4: Required vs Optional
        demonstrate_feature(
            "Required vs Optional Fields Clarity",
            RegistrationForm,
            "Clear distinction between required and optional fields with proper marking",
        ),
        # Feature 5: Examples and Documentation
        demonstrate_feature(
            "Examples and Documentation Support",
            APIRequest,
            "Rich examples that help LLMs understand expected data patterns",
        ),
        # Feature 6: Advanced Array Types - Contains
        demonstrate_feature(
            "Advanced Array Types - Contains Constraints",
            advanced_array_schemas["contains_constraint"],
            "Arrays with contains constraints and count limitations",
        ),
        # Feature 6: Advanced Array Types - Tuples
        demonstrate_feature(
            "Advanced Array Types - Enhanced Tuples",
            advanced_array_schemas["advanced_tuple"],
            "Tuples with additional items and descriptive constraints",
        ),
        demonstrate_feature(
            "Comprehensive User Model",
            ComprehensiveUserModel,
            "A comprehensive model showcasing all implemented features",
        ),
    ]

    md = "\n\n".join(texts)

    # save to docs/demo.md
    file = "docs/demo.md"
    with open(file, "w") as f:
        f.write(md)

    logger.info(f"Demo saved to '{file}'")


def on_startup(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
    logger.info("Running demo_features on startup")
    main()


if __name__ == "__main__":
    main()
