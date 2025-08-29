"""Tests for field constraints support in scheLLMa."""

from pydantic import BaseModel, Field

from schellma import pydantic_to_llm


class TestConstraints:
    """Test field constraints extraction and formatting."""

    def test_string_length_constraints(self):
        """Test string length constraints."""

        class ModelWithStringConstraints(BaseModel):
            password: str = Field(min_length=8, max_length=128, description="Password")
            username: str = Field(min_length=3, description="Username")
            bio: str = Field(max_length=500, description="Bio")

        result = pydantic_to_llm(ModelWithStringConstraints)

        assert "length: 8-128" in result
        assert "minLength: 3" in result
        assert "maxLength: 500" in result

    def test_string_pattern_constraints(self):
        """Test string pattern constraints with readable formats."""

        class ModelWithPatterns(BaseModel):
            email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Email")
            phone: str = Field(pattern=r"^\+?1?\d{9,15}$", description="Phone")
            username: str = Field(pattern=r"^[a-zA-Z0-9_]+$", description="Username")
            custom: str = Field(pattern=r"^[A-Z]{3}$", description="Custom pattern")

        result = pydantic_to_llm(ModelWithPatterns)

        assert "format: email" in result
        assert "format: phone" in result
        assert "pattern: alphanumeric and underscore only" in result
        assert "pattern: ^[A-Z]{3}$" in result

    def test_numeric_range_constraints(self):
        """Test numeric range constraints."""

        class ModelWithNumericConstraints(BaseModel):
            age: int = Field(ge=0, le=150, description="Age")
            score: float = Field(ge=0.0, le=100.0, description="Score")
            min_only: int = Field(ge=1, description="Minimum only")
            max_only: float = Field(le=999.99, description="Maximum only")

        result = pydantic_to_llm(ModelWithNumericConstraints)

        assert "range: 0-150" in result
        assert "range: 0.0-100.0" in result
        assert "minimum: 1" in result
        assert "maximum: 999.99" in result

    def test_numeric_multiple_constraints(self):
        """Test numeric multipleOf constraints."""

        class ModelWithMultipleConstraints(BaseModel):
            discount: float = Field(multiple_of=0.05, description="Discount")
            integer_only: int = Field(multiple_of=1, description="Integer")
            custom_multiple: float = Field(multiple_of=2.5, description="Custom")

        result = pydantic_to_llm(ModelWithMultipleConstraints)

        assert "multipleOf: 0.05 (5% increments)" in result
        assert "multipleOf: 1 (integers only)" in result
        assert "multipleOf: 2.5" in result

    def test_array_constraints(self):
        """Test array constraints."""

        class ModelWithArrayConstraints(BaseModel):
            tags: list[str] = Field(min_length=1, max_length=10, description="Tags")
            min_only: list[int] = Field(min_length=1, description="Minimum items")
            max_only: list[str] = Field(max_length=5, description="Maximum items")

        result = pydantic_to_llm(ModelWithArrayConstraints)

        assert "items: 1-10" in result
        assert "minItems: 1" in result
        assert "maxItems: 5" in result

    def test_combined_constraints(self):
        """Test fields with multiple constraints."""

        class ModelWithCombinedConstraints(BaseModel):
            username: str = Field(
                min_length=3,
                max_length=20,
                pattern=r"^[a-zA-Z0-9_]+$",
                description="Username",
            )
            rating: int = Field(ge=1, le=5, multiple_of=1, description="Rating")

        result = pydantic_to_llm(ModelWithCombinedConstraints)

        assert "length: 3-20" in result
        assert "pattern: alphanumeric and underscore only" in result
        assert "range: 1-5" in result
        assert "multipleOf: 1 (integers only)" in result

    def test_constraints_with_defaults(self):
        """Test constraints combined with default values."""

        class ModelWithConstraintsAndDefaults(BaseModel):
            name: str = Field(
                default="Anonymous", min_length=1, max_length=50, description="Name"
            )
            age: int = Field(default=0, ge=0, le=150, description="Age")

        result = pydantic_to_llm(ModelWithConstraintsAndDefaults)

        assert 'Name, default: "Anonymous", length: 1-50' in result
        assert "Age, default: 0, range: 0-150" in result

    def test_no_constraints(self):
        """Test fields without constraints work normally."""

        class ModelWithoutConstraints(BaseModel):
            simple_string: str = Field(description="Simple string")
            simple_int: int = Field(description="Simple integer")
            simple_array: list[str] = Field(description="Simple array")

        result = pydantic_to_llm(ModelWithoutConstraints)

        # Should only have descriptions, no constraint info
        assert "Simple string" in result
        assert "Simple integer" in result
        assert "Simple array" in result
        assert "length:" not in result
        assert "range:" not in result
        assert "pattern:" not in result

    def test_mixed_fields_with_and_without_constraints(self):
        """Test model with mix of constrained and unconstrained fields."""

        class MixedModel(BaseModel):
            constrained_string: str = Field(min_length=5, description="Constrained")
            simple_string: str = Field(description="Simple")
            constrained_int: int = Field(ge=0, le=100, description="Constrained int")
            simple_int: int = Field(description="Simple int")

        result = pydantic_to_llm(MixedModel)

        assert "Constrained, minLength: 5" in result
        assert "Simple" in result and "Simple, minLength:" not in result
        assert "Constrained int, range: 0-100" in result
        assert "Simple int" in result and "Simple int, range:" not in result

    def test_exclusive_constraints(self):
        """Test exclusive minimum and maximum constraints."""

        class ModelWithExclusiveConstraints(BaseModel):
            exclusive_min: float = Field(gt=0.0, description="Exclusive minimum")
            exclusive_max: float = Field(lt=100.0, description="Exclusive maximum")
            both_exclusive: float = Field(gt=0.0, lt=1.0, description="Both exclusive")

        result = pydantic_to_llm(ModelWithExclusiveConstraints)

        assert "exclusiveMinimum: 0.0" in result
        assert "exclusiveMaximum: 100.0" in result
        assert "exclusiveMinimum: 0.0, exclusiveMaximum: 1.0" in result
