"""Tests for examples support in scheLLMa."""

from pydantic import BaseModel, Field

from schellma import pydantic_to_schellma


class TestExamples:
    """Test examples extraction and formatting."""

    def test_single_example(self):
        """Test fields with single examples."""

        class ModelWithSingleExamples(BaseModel):
            name: str = Field(description="User name", examples=["John Doe"])
            age: int = Field(description="User age", examples=[25])
            is_active: bool = Field(description="Active status", examples=[True])

        result = pydantic_to_schellma(ModelWithSingleExamples)

        assert 'example: "John Doe"' in result
        assert "example: 25" in result
        assert "example: true" in result

    def test_multiple_examples(self):
        """Test fields with multiple examples."""

        class ModelWithMultipleExamples(BaseModel):
            method: str = Field(
                description="HTTP method", examples=["GET", "POST", "PUT"]
            )
            status_code: int = Field(
                description="Status code", examples=[200, 404, 500]
            )

        result = pydantic_to_schellma(ModelWithMultipleExamples)

        assert 'examples: "GET", "POST", "PUT"' in result
        assert "examples: 200, 404, 500" in result

    def test_many_examples_truncated(self):
        """Test that many examples are truncated with ellipsis."""

        class ModelWithManyExamples(BaseModel):
            color: str = Field(
                description="Color name",
                examples=["red", "blue", "green", "yellow", "purple", "orange"],
            )

        result = pydantic_to_schellma(ModelWithManyExamples)

        assert 'examples: "red", "blue", "green", ...' in result

    def test_complex_examples(self):
        """Test examples with complex data types."""

        class ModelWithComplexExamples(BaseModel):
            tags: list[str] = Field(description="Tags", examples=[["tag1", "tag2"]])
            config: dict[str, str] = Field(
                description="Config", examples=[{"theme": "dark", "lang": "en"}]
            )

        result = pydantic_to_schellma(ModelWithComplexExamples)

        assert 'example: ["tag1", "tag2"]' in result
        # Dictionary order may vary, so check for both possible orders
        assert (
            'example: { "theme": "dark", "lang": "en" }' in result
            or 'example: { "lang": "en", "theme": "dark" }' in result
        )

    def test_examples_with_defaults_and_constraints(self):
        """Test examples combined with defaults and constraints."""

        class ModelWithEverything(BaseModel):
            username: str = Field(
                default="anonymous",
                min_length=3,
                max_length=20,
                examples=["john_doe", "jane_smith"],
                description="Username",
            )
            age: int = Field(
                ge=0, le=150, examples=[25, 30, 35], description="User age"
            )

        result = pydantic_to_schellma(ModelWithEverything)

        assert (
            'Username, default: "anonymous", length: 3-20, examples: "john_doe", "jane_smith", optional'
            in result
        )
        assert "User age, range: 0-150, examples: 25, 30, 35, required" in result

    def test_no_examples(self):
        """Test fields without examples work normally."""

        class ModelWithoutExamples(BaseModel):
            name: str = Field(description="User name")
            age: int = Field(description="User age")

        result = pydantic_to_schellma(ModelWithoutExamples)

        assert "example:" not in result
        assert "examples:" not in result
        assert "User name, required" in result
        assert "User age, required" in result

    def test_mixed_fields_with_and_without_examples(self):
        """Test model with mix of fields with and without examples."""

        class MixedModel(BaseModel):
            with_examples: str = Field(description="Has examples", examples=["test"])
            without_examples: str = Field(description="No examples")

        result = pydantic_to_schellma(MixedModel)

        assert 'Has examples, example: "test", required' in result
        assert "No examples, required" in result
        assert "No examples, example:" not in result

    def test_empty_examples_list(self):
        """Test that empty examples list is ignored."""

        class ModelWithEmptyExamples(BaseModel):
            field: str = Field(description="Test field", examples=[])

        result = pydantic_to_schellma(ModelWithEmptyExamples)

        assert "example:" not in result
        assert "examples:" not in result

    def test_nullable_field_with_examples(self):
        """Test nullable fields with examples."""

        class ModelWithNullableExamples(BaseModel):
            optional_field: str | None = Field(
                default=None,
                description="Optional field",
                examples=["value1", "value2"],
            )

        result = pydantic_to_schellma(ModelWithNullableExamples)

        # Examples should be extracted from the non-null type in anyOf
        assert 'examples: "value1", "value2"' in result

    def test_examples_formatting_edge_cases(self):
        """Test examples formatting with various data types."""

        class ModelWithEdgeCases(BaseModel):
            null_example: str | None = Field(
                description="Null example", examples=[None]
            )
            bool_examples: bool = Field(
                description="Boolean examples", examples=[True, False]
            )
            float_examples: float = Field(
                description="Float examples", examples=[1.5, 2.7]
            )
            string_with_quotes: str = Field(
                description="String with quotes", examples=['He said "hello"']
            )

        result = pydantic_to_schellma(ModelWithEdgeCases)

        assert "example: null" in result
        assert "examples: true, false" in result
        assert "examples: 1.5, 2.7" in result
        # The string formatting doesn't escape quotes in the current implementation
        assert 'example: "He said "hello""' in result
