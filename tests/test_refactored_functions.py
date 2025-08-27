"""Test the refactored conversion functions."""

from schellma import json_schema_to_llm
from schellma.models import NestedModel


class TestRefactoredFunctions:
    """Test that refactored functions work correctly."""

    def test_string_type_conversion(self):
        """Test string type conversion."""
        schema = {"type": "string"}
        result = json_schema_to_llm(schema)
        assert result == "string"

    def test_enum_conversion(self):
        """Test enum conversion."""
        schema = {"type": "string", "enum": ["option1", "option2", "option3"]}
        result = json_schema_to_llm(schema)
        assert '"option1" | "option2" | "option3"' in result

    def test_array_conversion(self):
        """Test array conversion."""
        schema = {"type": "array", "items": {"type": "string"}}
        result = json_schema_to_llm(schema)
        assert "string[]" in result

    def test_tuple_conversion(self):
        """Test tuple conversion with prefixItems."""
        schema = {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "integer"}],
        }
        result = json_schema_to_llm(schema)
        assert "[string, int]" in result

    def test_object_conversion(self):
        """Test object conversion."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }
        result = json_schema_to_llm(schema)
        assert '"name": string' in result
        assert '"age": int' in result

    def test_additional_properties_conversion(self):
        """Test additionalProperties conversion."""
        schema = {"type": "object", "additionalProperties": {"type": "string"}}
        result = json_schema_to_llm(schema)
        assert "{ [key: string]: string }" in result

    def test_any_of_conversion(self):
        """Test anyOf conversion."""
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        result = json_schema_to_llm(schema)
        assert "string | int" in result

    def test_nullable_conversion(self):
        """Test nullable type conversion."""
        schema = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        result = json_schema_to_llm(schema)
        assert "string | null" in result

    def test_one_of_conversion(self):
        """Test oneOf conversion."""
        schema = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        result = json_schema_to_llm(schema)
        assert "string | int" in result

    def test_reference_conversion(self):
        """Test reference conversion."""
        schema = {
            "type": "object",
            "properties": {"nested": {"$ref": "#/$defs/NestedType"}},
            "$defs": {
                "NestedType": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                }
            },
        }
        result = json_schema_to_llm(schema, define_types=True)
        assert "NestedType" in result
        assert '"value": string' in result

    def test_complex_nested_structure(self):
        """Test complex nested structure conversion."""
        schema = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            },
        }
        result = json_schema_to_llm(schema)
        assert '"users": {' in result
        assert '"name": string' in result
        assert '"tags": string[]' in result

    def test_pydantic_model_still_works(self):
        """Test that Pydantic model conversion still works after refactoring."""
        from schellma import pydantic_to_llm

        result = pydantic_to_llm(NestedModel)
        assert "string" in result
        assert "int" in result
        assert '"text"' in result
        assert '"number"' in result

    def test_function_separation_maintains_behavior(self):
        """Test that function separation maintains original behavior."""
        # Test with a complex schema that exercises multiple functions
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "inactive"]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "optional_field": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
        }

        result = json_schema_to_llm(schema)

        # Verify all expected parts are present
        assert '"id": int' in result
        assert '"name": string' in result
        assert '"status": "active" | "inactive"' in result
        assert '"tags": string[]' in result
        assert '"metadata": { [key: string]: string }' in result
        assert '"optional_field": string | null' in result
