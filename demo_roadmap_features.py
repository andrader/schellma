#!/usr/bin/env python3
"""Demonstration of all the roadmap features implemented in scheLLMa."""

from pydantic import BaseModel, Field

from schellma import pydantic_to_llm


class ComprehensiveUserModel(BaseModel):
    """A comprehensive model showcasing all implemented roadmap features."""

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


if __name__ == "__main__":
    print("🎉 scheLLMa Roadmap Features Demonstration")
    print("=" * 60)
    print()

    print("📋 Implemented Features:")
    print("✅ 1. Default Values Support")
    print("✅ 2. Field Constraints with Human-Readable Comments")
    print("✅ 3. Required vs Optional Fields Clarity")
    print("✅ 4. Examples and Documentation Support")
    print()

    print("🔧 Generated TypeScript-like Schema:")
    print("-" * 40)
    result = pydantic_to_llm(ComprehensiveUserModel)
    print(result)

    print()
    print("🌟 Key Features Demonstrated:")
    print("• Default values shown in human-readable format")
    print("• String constraints (length, patterns) with smart formatting")
    print("• Numeric constraints (ranges, multiples) with clear descriptions")
    print("• Array constraints (item counts) with readable limits")
    print("• Required/optional field marking for clear API contracts")
    print("• Examples for better LLM understanding and human documentation")
    print("• Nullable type constraints properly extracted from union types")
    print("• Complex default values (objects, arrays) properly formatted")
    print()

    print("🚀 Perfect for LLM Integration:")
    print("• Concise, readable format reduces token usage")
    print("• Rich context helps LLMs understand field requirements")
    print("• Examples provide clear guidance for data generation")
    print("• Constraints prevent invalid data creation")
    print("• Human-readable comments improve prompt engineering")
