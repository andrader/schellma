"""Test error handling and validation."""

import pytest
from pydantic import BaseModel

from schellma.converters import (
    json_schema_to_llm,
    pydantic_to_llm,
)
from schellma.exceptions import (
    CircularReferenceError,
    ConversionError,
    InvalidSchemaError,
)


class TestInvalidSchemaError:
    """Test InvalidSchemaError cases."""

    def test_empty_schema(self):
        """Test that empty schema raises InvalidSchemaError."""
        with pytest.raises(InvalidSchemaError, match="Schema cannot be empty"):
            json_schema_to_llm({})

    def test_non_dict_schema(self):
        """Test that non-dict schema raises InvalidSchemaError."""
        with pytest.raises(InvalidSchemaError, match="Schema must be a dictionary"):
            json_schema_to_llm("not a dict")  # type: ignore

    def test_invalid_model_class(self):
        """Test that invalid model class raises InvalidSchemaError."""
        with pytest.raises(InvalidSchemaError, match="model_class must be a class"):
            pydantic_to_llm("not a class")  # type: ignore

    def test_non_basemodel_class(self):
        """Test that non-BaseModel class raises InvalidSchemaError."""

        class NotABaseModel:
            pass

        with pytest.raises(InvalidSchemaError, match="must be a BaseModel subclass"):
            pydantic_to_llm(NotABaseModel)  # type: ignore

    def test_invalid_defs_structure(self):
        """Test that invalid $defs structure raises InvalidSchemaError."""
        schema = {
            "type": "object",
            "properties": {"test": {"type": "string"}},
            "$defs": "not a dict",
        }
        with pytest.raises(InvalidSchemaError, match="\\$defs must be a dictionary"):
            json_schema_to_llm(schema)


class TestConversionError:
    """Test ConversionError cases."""

    def test_invalid_type_definition(self):
        """Test that invalid type definition raises ConversionError."""
        schema = {"type": "object", "properties": {"test": "not a dict"}}
        with pytest.raises(
            ConversionError, match="Property schema for 'test' must be a dictionary"
        ):
            json_schema_to_llm(schema)

    def test_invalid_ref_format(self):
        """Test that invalid $ref format raises ConversionError."""
        schema = {
            "type": "object",
            "properties": {"test": {"$ref": "invalid-ref-format"}},
        }
        with pytest.raises(ConversionError, match="Unsupported reference format"):
            json_schema_to_llm(schema)

    def test_non_string_ref(self):
        """Test that non-string $ref raises ConversionError."""
        schema = {"type": "object", "properties": {"test": {"$ref": 123}}}
        with pytest.raises(ConversionError, match="\\$ref must be a string"):
            json_schema_to_llm(schema)

    def test_invalid_prefix_items(self):
        """Test that invalid prefixItems raises ConversionError."""
        schema = {"type": "array", "prefixItems": "not a list"}
        with pytest.raises(ConversionError, match="prefixItems must be a list"):
            json_schema_to_llm(schema)

    def test_invalid_any_of(self):
        """Test that invalid anyOf raises ConversionError."""
        schema = {"anyOf": "not a list"}
        with pytest.raises(ConversionError, match="anyOf must be a list"):
            json_schema_to_llm(schema)

    def test_invalid_one_of(self):
        """Test that invalid oneOf raises ConversionError."""
        schema = {"oneOf": "not a list"}
        with pytest.raises(ConversionError, match="oneOf must be a list"):
            json_schema_to_llm(schema)

    def test_invalid_properties(self):
        """Test that invalid properties raises ConversionError."""
        schema = {"type": "object", "properties": "not a dict"}
        with pytest.raises(ConversionError, match="properties must be a dictionary"):
            json_schema_to_llm(schema)

    def test_invalid_property_name(self):
        """Test that invalid property name raises ConversionError."""
        schema = {"type": "object", "properties": {123: {"type": "string"}}}
        with pytest.raises(ConversionError, match="Property name must be a string"):
            json_schema_to_llm(schema)

    def test_invalid_additional_properties(self):
        """Test that invalid additionalProperties raises ConversionError."""
        schema = {"type": "object", "additionalProperties": "invalid"}
        with pytest.raises(ConversionError, match="Invalid additionalProperties value"):
            json_schema_to_llm(schema)

    def test_missing_definition(self):
        """Test that missing definition raises ConversionError."""
        schema = {
            "type": "object",
            "properties": {"test": {"$ref": "#/$defs/MissingType"}},
        }
        with pytest.raises(ConversionError, match="Definition 'MissingType' not found"):
            json_schema_to_llm(schema, define_types=False)


class TestCircularReferenceError:
    """Test CircularReferenceError cases."""

    def test_circular_reference_detection(self):
        """Test that circular references are detected."""
        # Create a schema with circular reference
        schema = {
            "type": "object",
            "properties": {"self_ref": {"$ref": "#/$defs/SelfRef"}},
            "$defs": {
                "SelfRef": {
                    "type": "object",
                    "properties": {"nested": {"$ref": "#/$defs/SelfRef"}},
                }
            },
        }

        # This should detect the circular reference when processing inline
        with pytest.raises(CircularReferenceError, match="Circular reference detected"):
            json_schema_to_llm(schema, define_types=False)


class TestValidInputs:
    """Test that valid inputs work correctly."""

    def test_valid_simple_schema(self):
        """Test that valid simple schema works."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }
        result = json_schema_to_llm(schema)
        assert "string" in result
        assert "int" in result

    def test_valid_pydantic_model(self):
        """Test that valid Pydantic model works."""

        class TestModel(BaseModel):
            name: str
            age: int

        result = pydantic_to_llm(TestModel)
        assert "string" in result
        assert "int" in result

    def test_enum_handling(self):
        """Test that enums are handled correctly."""
        schema = {"type": "string", "enum": ["option1", "option2", "option3"]}
        result = json_schema_to_llm(schema)
        assert '"option1" | "option2" | "option3"' in result

    def test_nullable_types(self):
        """Test that nullable types are handled correctly."""
        schema = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        result = json_schema_to_llm(schema)
        assert "string | null" in result
