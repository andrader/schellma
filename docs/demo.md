# 🎯 scheLLMa Complete Features Demonstration

This demonstrates ALL implemented features for LLM integration

## 🌟 Key Features

- Default values shown in human-readable format
- String constraints (length, patterns) with smart formatting
- Numeric constraints (ranges, multiples) with clear descriptions
- Array constraints (item counts) with readable limits
- Required/optional field marking for clear API contracts
- Examples for better LLM understanding and human documentation
- Nullable type constraints properly extracted from union types
- Complex default values (objects, arrays) properly formatted


## 🚀 Perfect for LLM Integration:
- Concise, readable format reduces token usage
- Rich context helps LLMs understand field requirements
- Examples provide clear guidance for data generation
- Constraints prevent invalid data creation
- Human-readable comments improve prompt engineering


## Default Values Support

Shows default values in human-readable comments for better LLM understanding
```python
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

```
```typescript
{
  // User display name, default: "Anonymous", optional
  "name": string,
  // User age in years, default: 0, minimum: 0, optional
  "age": int,
  // Account status, default: true, optional
  "active": boolean,
  // User tags, optional
  "tags": string[],
  // User preferences, optional
  "settings": { [key: string]: string },
}
```

## Field Constraints with Human-Readable Comments

Displays string, numeric, and array constraints in clear, readable format
```python
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

```
```typescript
{
  // Product name, length: 3-100, required
  "name": string,
  // Product SKU, pattern: ^[A-Z]{3}-\d{4}$, required
  "sku": string,
  // Contact email, format: email, required
  "email": string,
  // Product price, range: 0.01-999999.99, required
  "price": number,
  // Stock quantity, minimum: 1, required
  "quantity": int,
  // Discount percentage, multipleOf: 0.05 (5% increments), required
  "discount": number,
  // Product categories, items: 1-5, required
  "categories": string[],
  // Unique product tags, uniqueItems: true, required
  "tags": string[],
}
```

## Discriminated Union Types

Shows discriminated unions with clear type indicators
```python
class UserOrAdmin(BaseModel):
    entity: User | Admin = Field(discriminator="type")

```
```typescript
Admin {
  // default: "admin", optional
  "type": string,
  // required
  "name": string,
  // required
  "permissions": string[],
}

User {
  // default: "user", optional
  "type": string,
  // required
  "name": string,
  // required
  "email": string,
}



{
  // required
  "entity": User // type: "user" | Admin // type: "admin",
}
```

## Inheritance (allOf-like behavior)

Demonstrates inheritance patterns that work like allOf intersections
```python
class ExtendedUser(BaseEntity):
    name: str = Field(description="User name")
    email: str = Field(description="User email")

```
```typescript
{
  // Unique identifier, required
  "id": string,
  // Creation timestamp, required
  "created_at": string,
  // User name, required
  "name": string,
  // User email, required
  "email": string,
}
```

## allOf Intersection Types

Direct allOf schema merging with intersection comments
```json
{
  "type": "object",
  "allOf": [
    {
      "type": "object",
      "description": "Base fields",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique ID"
        },
        "created": {
          "type": "string",
          "description": "Creation time"
        }
      },
      "required": [
        "id",
        "created"
      ]
    },
    {
      "type": "object",
      "description": "User fields",
      "properties": {
        "name": {
          "type": "string",
          "description": "User name"
        },
        "email": {
          "type": "string",
          "description": "User email"
        }
      },
      "required": [
        "name",
        "email"
      ]
    }
  ]
}
```
```typescript
{
  // Intersection of: Base fields, User fields
  // Unique ID, required
  "id": string,
  // Creation time, required
  "created": string,
  // User name, required
  "name": string,
  // User email, required
  "email": string,
}
```

## NOT Constraints

Exclusion constraints with human-readable descriptions
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "not": {
        "enum": [
          "forbidden",
          "banned",
          "deleted"
        ]
      },
      "description": "Any status except forbidden values"
    }
  }
}
```
```typescript
{
  // Any status except forbidden values, not: "forbidden", "banned", "deleted", optional
  "status": string,
}
```

## Required vs Optional Fields Clarity

Clear distinction between required and optional fields with proper marking
```python
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

```
```typescript
{
  // Username for login, required
  "username": string,
  // Email address, required
  "email": string,
  // Account password, minLength: 8, required
  "password": string,
  // Full display name, default: null, optional
  "full_name": string | null,
  // User age, default: null, range: 13-120, optional
  "age": int | null,
  // User biography, default: null, maxLength: 500, optional
  "bio": string | null,
}
```

## Examples and Documentation Support

Rich examples that help LLMs understand expected data patterns
```python
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

```
```typescript
{
  // HTTP method, examples: "GET", "POST", "PUT", ..., required
  "method": string,
  // Request URL, examples: "https://api.example.com/users", "https://api.example.com/products/123", required
  "url": string,
  // Request headers, default: null, example: { "Authorization": "Bearer token123", "Content-Type": "application/json" }, optional
  "headers": { [key: string]: string } | null,
  // Request body, default: null, example: { "email": "john@example.com", "name": "John Doe" }, optional
  "body": { [key: string]: any } | null,
}
```

## Advanced Array Types - Contains Constraints

Arrays with contains constraints and count limitations
```json
{
  "type": "object",
  "properties": {
    "required_tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "contains": {
        "type": "string",
        "pattern": "^required_"
      },
      "minContains": 1,
      "maxContains": 3,
      "description": "Array must contain 1-3 items starting with 'required_'"
    }
  }
}
```
```typescript
{
  // Array must contain 1-3 items starting with 'required_', contains: string starting with 'required_', contains: 1-3 items, optional
  "required_tags": string[],
}
```

## Advanced Array Types - Enhanced Tuples

Tuples with additional items and descriptive constraints
```json
{
  "type": "object",
  "properties": {
    "coordinates": {
      "type": "array",
      "prefixItems": [
        {
          "type": "number",
          "description": "latitude"
        },
        {
          "type": "number",
          "description": "longitude"
        }
      ],
      "items": {
        "type": "number"
      },
      "minItems": 2,
      "maxItems": 4,
      "description": "Coordinates with optional elevation and accuracy"
    }
  }
}
```
```typescript
{
  // Coordinates with optional elevation and accuracy, items: 2-4, optional
  "coordinates": [number, number, ...number[]],
}
```

## Comprehensive User Model

A comprehensive model showcasing all implemented features
```python
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

```
```typescript
{
  // Unique username for the account, length: 3-20, pattern: alphanumeric and underscore only, examples: "john_doe", "jane_smith", "user123", required
  "username": string,
  // User's email address, format: email, examples: "john@example.com", "jane@company.org", required
  "email": string,
  // Display name for the user, default: "Anonymous User", length: 1-100, examples: "John Doe", "Jane Smith", optional
  "name": string,
  // User's age in years, default: 18, range: 13-120, examples: 25, 30, 35, optional
  "age": int,
  // User's biography, default: null, maxLength: 500, examples: "Software developer passionate about AI", "Love hiking and photography", optional
  "bio": string | null,
  // User's phone number, default: null, format: phone, examples: "+1-555-123-4567", "+44-20-7946-0958", optional
  "phone": string | null,
  // User interest tags, items: 0-10, examples: ["python", "ai", "music"], ["travel", "photography"], optional
  "tags": string[],
  // User's reputation score, default: 0.0, range: 0.0-100.0, examples: 85.5, 92.3, 78.1, optional
  "score": number,
  // User's star rating, default: 5, range: 1-5, multipleOf: 1 (integers only), examples: 4, 5, optional
  "rating": int,
  // User preferences and settings, default: { "theme": "dark", "language": "en", "timezone": "UTC" }, examples: { "language": "es", "theme": "light" }, { "language": "fr", "theme": "dark" }, optional
  "preferences": { [key: string]: string },
}
```