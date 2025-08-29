"""Tests for default values support in scheLLMa."""

from pydantic import BaseModel, Field

from schellma import pydantic_to_schellma


class TestDefaultValues:
    """Test default values extraction and formatting."""

    def test_basic_default_values(self):
        """Test basic default value types."""

        class ModelWithDefaults(BaseModel):
            name: str = Field(default="Anonymous", description="User name")
            age: int = Field(default=0, description="User age")
            is_active: bool = Field(default=True, description="Active status")
            score: float = Field(default=0.0, description="User score")

        result = pydantic_to_schellma(ModelWithDefaults)

        assert 'default: "Anonymous"' in result
        assert "default: 0" in result
        assert "default: true" in result
        assert "default: 0.0" in result

    def test_null_default_values(self):
        """Test null default values."""

        class ModelWithNullDefaults(BaseModel):
            optional_field: str | None = Field(
                default=None, description="Optional field"
            )

        result = pydantic_to_schellma(ModelWithNullDefaults)

        assert "default: null" in result

    def test_complex_default_values(self):
        """Test complex default values like lists and dicts."""

        class ModelWithComplexDefaults(BaseModel):
            tags: list[str] = Field(default=["tag1", "tag2"], description="User tags")
            config: dict[str, str] = Field(
                default={"theme": "dark", "lang": "en"}, description="User config"
            )
            empty_list: list[int] = Field(default=[], description="Empty list")
            empty_dict: dict[str, str] = Field(default={}, description="Empty dict")

        result = pydantic_to_schellma(ModelWithComplexDefaults)

        assert 'default: ["tag1", "tag2"]' in result
        assert 'default: { "theme": "dark", "lang": "en" }' in result
        assert "default: []" in result
        assert "default: {}" in result

    def test_nested_complex_defaults(self):
        """Test nested complex default values."""

        class ModelWithNestedDefaults(BaseModel):
            nested_list: list[list[str]] = Field(
                default=[["a", "b"], ["c", "d"]], description="Nested list"
            )
            nested_dict: dict[str, dict[str, int]] = Field(
                default={"section1": {"count": 1}, "section2": {"count": 2}},
                description="Nested dict",
            )

        result = pydantic_to_schellma(ModelWithNestedDefaults)

        assert 'default: [["a", "b"], ["c", "d"]]' in result
        assert (
            'default: { "section1": { "count": 1 }, "section2": { "count": 2 } }'
            in result
        )

    def test_description_and_default_combination(self):
        """Test that description and default are properly combined."""

        class ModelWithBoth(BaseModel):
            field_with_both: str = Field(default="test", description="A test field")
            field_with_description_only: str = Field(description="Description only")

        result = pydantic_to_schellma(ModelWithBoth)

        # Should have both description and default
        assert 'A test field, default: "test"' in result
        # Should have only description
        assert "Description only" in result
        assert "Description only, default:" not in result

    def test_no_description_with_default(self):
        """Test fields with default but no description."""

        class ModelWithDefaultOnly(BaseModel):
            field_with_default_only: str = Field(default="value")

        result = pydantic_to_schellma(ModelWithDefaultOnly)

        assert 'default: "value"' in result

    def test_field_without_defaults(self):
        """Test that fields without defaults work normally."""

        class ModelWithoutDefaults(BaseModel):
            required_field: str = Field(description="Required field")
            another_field: int

        result = pydantic_to_schellma(ModelWithoutDefaults)

        assert "default:" not in result
        assert "Required field" in result

    def test_mixed_fields(self):
        """Test model with mix of fields with and without defaults."""

        class MixedModel(BaseModel):
            with_default: str = Field(default="test", description="Has default")
            without_default: str = Field(description="No default")
            default_only: int = Field(default=42)
            description_only: bool = Field(description="Only description")
            plain_field: float

        result = pydantic_to_schellma(MixedModel)

        assert 'Has default, default: "test"' in result
        assert "No default" in result and "No default, default:" not in result
        assert "default: 42" in result
        assert (
            "Only description" in result and "Only description, default:" not in result
        )
        # Plain field should have a comment showing it's required (since all fields now have required/optional status)
        assert "required" in result  # Plain field will be marked as required
