# **scheLLMa**: Features Demonstration

This demonstrates some of the implemented features:

## Key Features

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


## Default Values Support

Shows default values in human-readable comments for better LLM understanding

<div class="grid" markdown>

!!! note "Pydantic"
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


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (95 tokens)"
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
    === "JSON Schema (239 tokens)"
        ```json
        {
          "description": "User profile with comprehensive default values.",
          "properties": {
            "name": {
              "default": "Anonymous",
              "description": "User display name",
              "title": "Name",
              "type": "string"
            },
            "age": {
              "default": 0,
              "description": "User age in years",
              "minimum": 0,
              "title": "Age",
              "type": "integer"
            },
            "active": {
              "default": true,
              "description": "Account status",
              "title": "Active",
              "type": "boolean"
            },
            "tags": {
              "description": "User tags",
              "items": {
                "type": "string"
              },
              "title": "Tags",
              "type": "array"
            },
            "settings": {
              "additionalProperties": {
                "type": "string"
              },
              "description": "User preferences",
              "title": "Settings",
              "type": "object"
            }
          },
          "title": "UserProfile",
          "type": "object"
        }
        ```



</div>


## Field Constraints with Human-Readable Comments

Displays string, numeric, and array constraints in clear, readable format

<div class="grid" markdown>

!!! note "Pydantic"
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


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (174 tokens)"
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
    === "JSON Schema (446 tokens)"
        ```json
        {
          "description": "Product with comprehensive field constraints.",
          "properties": {
            "name": {
              "description": "Product name",
              "maxLength": 100,
              "minLength": 3,
              "title": "Name",
              "type": "string"
            },
            "sku": {
              "description": "Product SKU",
              "pattern": "^[A-Z]{3}-\\d{4}$",
              "title": "Sku",
              "type": "string"
            },
            "email": {
              "description": "Contact email",
              "pattern": "^[^@]+@[^@]+\\.[^@]+$",
              "title": "Email",
              "type": "string"
            },
            "price": {
              "description": "Product price",
              "maximum": 999999.99,
              "minimum": 0.01,
              "title": "Price",
              "type": "number"
            },
            "quantity": {
              "description": "Stock quantity",
              "minimum": 1,
              "title": "Quantity",
              "type": "integer"
            },
            "discount": {
              "description": "Discount percentage",
              "multipleOf": 0.05,
              "title": "Discount",
              "type": "number"
            },
            "categories": {
              "description": "Product categories",
              "items": {
                "type": "string"
              },
              "maxItems": 5,
              "minItems": 1,
              "title": "Categories",
              "type": "array"
            },
            "tags": {
              "description": "Unique product tags",
              "items": {
                "type": "string"
              },
              "title": "Tags",
              "type": "array",
              "uniqueItems": true
            }
          },
          "required": [
            "name",
            "sku",
            "email",
            "price",
            "quantity",
            "discount",
            "categories",
            "tags"
          ],
          "title": "ProductModel",
          "type": "object"
        }
        ```



</div>


## Discriminated Union Types

Shows discriminated unions with clear type indicators

<div class="grid" markdown>

!!! note "Pydantic"
    ```python
    class UserOrAdmin(BaseModel):
        entity: User | Admin = Field(discriminator="type")

    ```


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (101 tokens)"
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
    === "JSON Schema (385 tokens)"
        ```json
        {
          "$defs": {
            "Admin": {
              "properties": {
                "type": {
                  "const": "admin",
                  "default": "admin",
                  "title": "Type",
                  "type": "string"
                },
                "name": {
                  "title": "Name",
                  "type": "string"
                },
                "permissions": {
                  "items": {
                    "type": "string"
                  },
                  "title": "Permissions",
                  "type": "array"
                }
              },
              "required": [
                "name",
                "permissions"
              ],
              "title": "Admin",
              "type": "object"
            },
            "User": {
              "properties": {
                "type": {
                  "const": "user",
                  "default": "user",
                  "title": "Type",
                  "type": "string"
                },
                "name": {
                  "title": "Name",
                  "type": "string"
                },
                "email": {
                  "title": "Email",
                  "type": "string"
                }
              },
              "required": [
                "name",
                "email"
              ],
              "title": "User",
              "type": "object"
            }
          },
          "properties": {
            "entity": {
              "discriminator": {
                "mapping": {
                  "admin": "#/$defs/Admin",
                  "user": "#/$defs/User"
                },
                "propertyName": "type"
              },
              "oneOf": [
                {
                  "$ref": "#/$defs/User"
                },
                {
                  "$ref": "#/$defs/Admin"
                }
              ],
              "title": "Entity"
            }
          },
          "required": [
            "entity"
          ],
          "title": "UserOrAdmin",
          "type": "object"
        }
        ```



</div>


## Inheritance (allOf-like behavior)

Demonstrates inheritance patterns that work like allOf intersections

<div class="grid" markdown>

!!! note "Pydantic"
    ```python
    class ExtendedUser(BaseEntity):
        name: str = Field(description="User name")
        email: str = Field(description="User email")

    ```


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (55 tokens)"
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
    === "JSON Schema (166 tokens)"
        ```json
        {
          "properties": {
            "id": {
              "description": "Unique identifier",
              "title": "Id",
              "type": "string"
            },
            "created_at": {
              "description": "Creation timestamp",
              "title": "Created At",
              "type": "string"
            },
            "name": {
              "description": "User name",
              "title": "Name",
              "type": "string"
            },
            "email": {
              "description": "User email",
              "title": "Email",
              "type": "string"
            }
          },
          "required": [
            "id",
            "created_at",
            "name",
            "email"
          ],
          "title": "ExtendedUser",
          "type": "object"
        }
        ```



</div>


## allOf Intersection Types

Direct allOf schema merging with intersection comments

<div class="grid" markdown>

!!! note "JSON Schema (187 tokens)"
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


!!! tip "ScheLLMa (65 tokens)"
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


</div>


## NOT Constraints

Exclusion constraints with human-readable descriptions

<div class="grid" markdown>

!!! note "JSON Schema (69 tokens)"
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


!!! tip "ScheLLMa (31 tokens)"
    ```typescript
    {
      // Any status except forbidden values, not: "forbidden", "banned", "deleted", optional
      "status": string,
    }
    ```


</div>


## Required vs Optional Fields Clarity

Clear distinction between required and optional fields with proper marking

<div class="grid" markdown>

!!! note "Pydantic"
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


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (118 tokens)"
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
    === "JSON Schema (351 tokens)"
        ```json
        {
          "description": "Registration form with clear required/optional distinction.",
          "properties": {
            "username": {
              "description": "Username for login",
              "title": "Username",
              "type": "string"
            },
            "email": {
              "description": "Email address",
              "title": "Email",
              "type": "string"
            },
            "password": {
              "description": "Account password",
              "minLength": 8,
              "title": "Password",
              "type": "string"
            },
            "full_name": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "Full display name",
              "title": "Full Name"
            },
            "age": {
              "anyOf": [
                {
                  "maximum": 120,
                  "minimum": 13,
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "User age",
              "title": "Age"
            },
            "bio": {
              "anyOf": [
                {
                  "maxLength": 500,
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "User biography",
              "title": "Bio"
            }
          },
          "required": [
            "username",
            "email",
            "password"
          ],
          "title": "RegistrationForm",
          "type": "object"
        }
        ```



</div>


## Examples and Documentation Support

Rich examples that help LLMs understand expected data patterns

<div class="grid" markdown>

!!! note "Pydantic"
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


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (151 tokens)"
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
    === "JSON Schema (353 tokens)"
        ```json
        {
          "description": "API request with rich examples.",
          "properties": {
            "method": {
              "description": "HTTP method",
              "examples": [
                "GET",
                "POST",
                "PUT",
                "DELETE"
              ],
              "title": "Method",
              "type": "string"
            },
            "url": {
              "description": "Request URL",
              "examples": [
                "https://api.example.com/users",
                "https://api.example.com/products/123"
              ],
              "title": "Url",
              "type": "string"
            },
            "headers": {
              "anyOf": [
                {
                  "additionalProperties": {
                    "type": "string"
                  },
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "Request headers",
              "examples": [
                {
                  "Authorization": "Bearer token123",
                  "Content-Type": "application/json"
                }
              ],
              "title": "Headers"
            },
            "body": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "Request body",
              "examples": [
                {
                  "email": "john@example.com",
                  "name": "John Doe"
                }
              ],
              "title": "Body"
            }
          },
          "required": [
            "method",
            "url"
          ],
          "title": "APIRequest",
          "type": "object"
        }
        ```



</div>


## Advanced Array Types - Contains Constraints

Arrays with contains constraints and count limitations

<div class="grid" markdown>

!!! note "JSON Schema (102 tokens)"
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


!!! tip "ScheLLMa (42 tokens)"
    ```typescript
    {
      // Array must contain 1-3 items starting with 'required_', contains: string starting with 'required_', contains: 1-3 items, optional
      "required_tags": string[],
    }
    ```


</div>


## Advanced Array Types - Enhanced Tuples

Tuples with additional items and descriptive constraints

<div class="grid" markdown>

!!! note "JSON Schema (116 tokens)"
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


!!! tip "ScheLLMa (33 tokens)"
    ```typescript
    {
      // Coordinates with optional elevation and accuracy, items: 2-4, optional
      "coordinates": [number, number, ...number[]],
    }
    ```


</div>


## Comprehensive User Model

A comprehensive model showcasing all implemented features

<div class="grid" markdown>

!!! note "Pydantic"
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


!!! note "ScheLLMa vs JSON Schema"
    === "ScheLLMa (455 tokens)"
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
    === "JSON Schema (923 tokens)"
        ```json
        {
          "description": "A comprehensive model showcasing all implemented features.",
          "properties": {
            "username": {
              "description": "Unique username for the account",
              "examples": [
                "john_doe",
                "jane_smith",
                "user123"
              ],
              "maxLength": 20,
              "minLength": 3,
              "pattern": "^[a-zA-Z0-9_]+$",
              "title": "Username",
              "type": "string"
            },
            "email": {
              "description": "User's email address",
              "examples": [
                "john@example.com",
                "jane@company.org"
              ],
              "pattern": "^[^@]+@[^@]+\\.[^@]+$",
              "title": "Email",
              "type": "string"
            },
            "name": {
              "default": "Anonymous User",
              "description": "Display name for the user",
              "examples": [
                "John Doe",
                "Jane Smith"
              ],
              "maxLength": 100,
              "minLength": 1,
              "title": "Name",
              "type": "string"
            },
            "age": {
              "default": 18,
              "description": "User's age in years",
              "examples": [
                25,
                30,
                35
              ],
              "maximum": 120,
              "minimum": 13,
              "title": "Age",
              "type": "integer"
            },
            "bio": {
              "anyOf": [
                {
                  "maxLength": 500,
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "User's biography",
              "examples": [
                "Software developer passionate about AI",
                "Love hiking and photography"
              ],
              "title": "Bio"
            },
            "phone": {
              "anyOf": [
                {
                  "pattern": "^\\+?1?\\d{9,15}$",
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "description": "User's phone number",
              "examples": [
                "+1-555-123-4567",
                "+44-20-7946-0958"
              ],
              "title": "Phone"
            },
            "tags": {
              "description": "User interest tags",
              "examples": [
                [
                  "python",
                  "ai",
                  "music"
                ],
                [
                  "travel",
                  "photography"
                ]
              ],
              "items": {
                "type": "string"
              },
              "maxItems": 10,
              "minItems": 0,
              "title": "Tags",
              "type": "array"
            },
            "score": {
              "default": 0.0,
              "description": "User's reputation score",
              "examples": [
                85.5,
                92.3,
                78.1
              ],
              "maximum": 100.0,
              "minimum": 0.0,
              "title": "Score",
              "type": "number"
            },
            "rating": {
              "default": 5,
              "description": "User's star rating",
              "examples": [
                4,
                5
              ],
              "maximum": 5,
              "minimum": 1,
              "multipleOf": 1,
              "title": "Rating",
              "type": "integer"
            },
            "preferences": {
              "additionalProperties": {
                "type": "string"
              },
              "default": {
                "theme": "dark",
                "language": "en",
                "timezone": "UTC"
              },
              "description": "User preferences and settings",
              "examples": [
                {
                  "language": "es",
                  "theme": "light"
                },
                {
                  "language": "fr",
                  "theme": "dark"
                }
              ],
              "title": "Preferences",
              "type": "object"
            }
          },
          "required": [
            "username",
            "email"
          ],
          "title": "ComprehensiveUserModel",
          "type": "object"
        }
        ```



</div>
