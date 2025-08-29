#!/usr/bin/env python3
"""
Complete Roadmap Features Demonstration

This script demonstrates ALL implemented roadmap features:
1. ✅ Default Values Support
2. ✅ Field Constraints with Human-Readable Comments
3. ✅ Advanced Union Types with Clear Descriptions
4. ✅ Required vs Optional Fields Clarity
5. ✅ Examples and Documentation Support
6. ✅ Advanced Array Types with Descriptions

Perfect for understanding scheLLMa's full capabilities for LLM integration.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from schellma import json_schema_to_llm, pydantic_to_llm


# === 1. DEFAULT VALUES SUPPORT ===
class UserProfile(BaseModel):
    """User profile with comprehensive default values."""

    name: str = Field(default="Anonymous", description="User display name")
    age: int = Field(default=0, description="User age in years")
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


def demonstrate_feature(title: str, model_or_schema: Any, description: str) -> None:
    """Demonstrate a specific feature with clear output."""
    print(f"\n{'=' * 60}")
    print(f"🚀 {title}")
    print(f"{'=' * 60}")
    print(f"📝 {description}")
    print("\n💡 Generated TypeScript-like Schema:")
    print("-" * 40)

    if isinstance(model_or_schema, dict):
        # It's a JSON schema
        result = json_schema_to_llm(model_or_schema)
    else:
        # It's a Pydantic model
        result = pydantic_to_llm(model_or_schema)

    print(result)


if __name__ == "__main__":
    print("🎯 scheLLMa Complete Roadmap Features Demonstration")
    print("=" * 60)
    print("This demonstrates ALL implemented roadmap features for LLM integration")

    # Feature 1: Default Values
    demonstrate_feature(
        "1. Default Values Support",
        UserProfile,
        "Shows default values in human-readable comments for better LLM understanding",
    )

    # Feature 2: Field Constraints
    demonstrate_feature(
        "2. Field Constraints with Human-Readable Comments",
        ProductModel,
        "Displays string, numeric, and array constraints in clear, readable format",
    )

    # Feature 3: Advanced Union Types - Discriminated Union
    demonstrate_feature(
        "3a. Discriminated Union Types",
        UserOrAdmin,
        "Shows discriminated unions with clear type indicators",
    )

    # Feature 3: Advanced Union Types - Inheritance (allOf-like)
    demonstrate_feature(
        "3b. Inheritance (allOf-like behavior)",
        ExtendedUser,
        "Demonstrates inheritance patterns that work like allOf intersections",
    )

    # Feature 3: Advanced Union Types - Direct allOf
    demonstrate_feature(
        "3c. allOf Intersection Types",
        advanced_array_schemas["allof_intersection"],
        "Direct allOf schema merging with intersection comments",
    )

    # Feature 3: Advanced Union Types - not constraints
    demonstrate_feature(
        "3d. NOT Constraints",
        advanced_array_schemas["not_constraint"],
        "Exclusion constraints with human-readable descriptions",
    )

    # Feature 4: Required vs Optional
    demonstrate_feature(
        "4. Required vs Optional Fields Clarity",
        RegistrationForm,
        "Clear distinction between required and optional fields with proper marking",
    )

    # Feature 5: Examples and Documentation
    demonstrate_feature(
        "5. Examples and Documentation Support",
        APIRequest,
        "Rich examples that help LLMs understand expected data patterns",
    )

    # Feature 6: Advanced Array Types - Contains
    demonstrate_feature(
        "6a. Advanced Array Types - Contains Constraints",
        advanced_array_schemas["contains_constraint"],
        "Arrays with contains constraints and count limitations",
    )

    # Feature 6: Advanced Array Types - Tuples
    demonstrate_feature(
        "6b. Advanced Array Types - Enhanced Tuples",
        advanced_array_schemas["advanced_tuple"],
        "Tuples with additional items and descriptive constraints",
    )

    print(f"\n{'=' * 60}")
    print("🎉 ALL ROADMAP FEATURES SUCCESSFULLY IMPLEMENTED!")
    print("=" * 60)
    print("✅ Default Values Support")
    print("✅ Field Constraints with Human-Readable Comments")
    print("✅ Advanced Union Types (allOf, not, discriminated)")
    print("✅ Required vs Optional Fields Clarity")
    print("✅ Examples and Documentation Support")
    print("✅ Advanced Array Types (contains, tuples)")
    print("\n🚀 scheLLMa is now fully optimized for LLM integration!")
    print(
        "   Perfect for generating schemas that LLMs can easily understand and follow."
    )
