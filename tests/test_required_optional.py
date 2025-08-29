"""Tests for required vs optional fields support in scheLLMa."""

from pydantic import BaseModel, Field

from schellma import pydantic_to_schellma


class TestRequiredOptional:
    """Test required vs optional field marking."""

    def test_required_fields(self):
        """Test that required fields are marked as required."""

        class ModelWithRequired(BaseModel):
            name: str = Field(description="User name")
            email: str = Field(description="User email")
            age: int = Field(description="User age")

        result = pydantic_to_schellma(ModelWithRequired)

        # All fields should be marked as required
        assert "User name, required" in result
        assert "User email, required" in result
        assert "User age, required" in result

    def test_optional_fields_with_defaults(self):
        """Test that fields with defaults are marked as optional."""

        class ModelWithDefaults(BaseModel):
            name: str = Field(default="Anonymous", description="User name")
            age: int = Field(default=0, description="User age")
            is_active: bool = Field(default=True, description="Active status")

        result = pydantic_to_schellma(ModelWithDefaults)

        # All fields should be marked as optional
        assert 'User name, default: "Anonymous", optional' in result
        assert "User age, default: 0, optional" in result
        assert "Active status, default: true, optional" in result

    def test_optional_nullable_fields(self):
        """Test that nullable fields are marked as optional."""

        class ModelWithNullable(BaseModel):
            phone: str | None = Field(default=None, description="Phone number")
            avatar: str | None = Field(description="Avatar URL")

        result = pydantic_to_schellma(ModelWithNullable)

        # Fields should be marked as optional
        assert "Phone number, default: null, optional" in result
        assert (
            "Avatar URL, required" in result
        )  # This one is actually required even though nullable

    def test_mixed_required_optional(self):
        """Test model with mix of required and optional fields."""

        class MixedModel(BaseModel):
            # Required fields
            name: str = Field(description="User name")
            email: str = Field(description="User email")

            # Optional fields with defaults
            age: int = Field(default=0, description="User age")
            bio: str = Field(default="", description="User bio")

            # Optional nullable fields
            phone: str | None = Field(default=None, description="Phone number")
            website: str | None = Field(description="Website URL")

        result = pydantic_to_schellma(MixedModel)

        # Required fields
        assert "User name, required" in result
        assert "User email, required" in result

        # Optional fields with defaults
        assert "User age, default: 0, optional" in result
        assert 'User bio, default: "", optional' in result
        assert "Phone number, default: null, optional" in result

        # Required nullable field
        assert "Website URL, required" in result

    def test_required_optional_with_constraints(self):
        """Test required/optional marking combined with constraints."""

        class ModelWithConstraints(BaseModel):
            username: str = Field(min_length=3, max_length=20, description="Username")
            password: str = Field(default="", min_length=8, description="Password")
            age: int | None = Field(default=None, ge=0, le=150, description="Age")

        result = pydantic_to_schellma(ModelWithConstraints)

        assert "Username, length: 3-20, required" in result
        assert 'Password, default: "", minLength: 8, optional' in result
        assert "Age, default: null, range: 0-150, optional" in result

    def test_no_description_fields(self):
        """Test fields without descriptions still get required/optional marking."""

        class ModelWithoutDescriptions(BaseModel):
            required_field: str
            optional_field: str = Field(default="test")

        result = pydantic_to_schellma(ModelWithoutDescriptions)

        assert "required" in result
        assert "optional" in result
        assert 'default: "test"' in result

    def test_all_required_fields(self):
        """Test model where all fields are required."""

        class AllRequiredModel(BaseModel):
            field1: str = Field(description="Field 1")
            field2: int = Field(description="Field 2")
            field3: bool = Field(description="Field 3")
            field4: str | None = Field(description="Field 4")  # Required nullable

        result = pydantic_to_schellma(AllRequiredModel)

        # All fields should be marked as required
        required_count = result.count("required")
        assert required_count == 4

    def test_all_optional_fields(self):
        """Test model where all fields are optional."""

        class AllOptionalModel(BaseModel):
            field1: str = Field(default="test1", description="Field 1")
            field2: int = Field(default=42, description="Field 2")
            field3: bool = Field(default=True, description="Field 3")
            field4: str | None = Field(default=None, description="Field 4")

        result = pydantic_to_schellma(AllOptionalModel)

        # All fields should be marked as optional
        optional_count = result.count("optional")
        assert optional_count == 4

    def test_complex_model_required_optional(self):
        """Test complex model with nested structures and required/optional fields."""

        class NestedModel(BaseModel):
            nested_field: str = Field(description="Nested field")

        class ComplexModel(BaseModel):
            required_string: str = Field(description="Required string")
            optional_string: str = Field(
                default="default", description="Optional string"
            )
            required_nested: NestedModel = Field(description="Required nested")
            optional_nested: NestedModel | None = Field(
                default=None, description="Optional nested"
            )

        result = pydantic_to_schellma(ComplexModel)

        assert "Required string, required" in result
        assert 'Optional string, default: "default", optional' in result
        assert "Required nested, required" in result
        assert "Optional nested, default: null, optional" in result
