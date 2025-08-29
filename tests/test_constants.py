"""Test constants extraction and usage."""

from schellma import json_schema_to_schellma
from schellma.constants import (
    DEFS_PREFIX,
    ENUM_VALUE_TEMPLATE,
    TS_ANY_TYPE,
    TS_ARRAY_TEMPLATE,
    TS_INDEX_SIGNATURE_ANY,
    TS_NULL_TYPE,
    TS_TUPLE_TEMPLATE,
    TS_TYPE_MAPPINGS,
    TS_UNION_SEPARATOR,
)


class TestConstants:
    """Test that constants are used correctly."""

    def test_type_mappings(self):
        """Test that type mappings work correctly."""
        schema = {"type": "string"}
        result = json_schema_to_schellma(schema)
        assert result == TS_TYPE_MAPPINGS["string"]

        schema = {"type": "integer"}
        result = json_schema_to_schellma(schema)
        assert result == TS_TYPE_MAPPINGS["integer"]

        schema = {"type": "number"}
        result = json_schema_to_schellma(schema)
        assert result == TS_TYPE_MAPPINGS["number"]

        schema = {"type": "boolean"}
        result = json_schema_to_schellma(schema)
        assert result == TS_TYPE_MAPPINGS["boolean"]

    def test_array_template(self):
        """Test that array template is used correctly."""
        schema = {"type": "array", "items": {"type": "string"}}
        result = json_schema_to_schellma(schema)
        expected = TS_ARRAY_TEMPLATE.format(type=TS_TYPE_MAPPINGS["string"])
        assert result == expected

    def test_tuple_template(self):
        """Test that tuple template is used correctly."""
        schema = {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "integer"}],
        }
        result = json_schema_to_schellma(schema)
        expected = TS_TUPLE_TEMPLATE.format(
            types=f"{TS_TYPE_MAPPINGS['string']}, {TS_TYPE_MAPPINGS['integer']}"
        )
        assert result == expected

    def test_enum_template(self):
        """Test that enum template is used correctly."""
        schema = {"type": "string", "enum": ["option1", "option2"]}
        result = json_schema_to_schellma(schema)
        expected = TS_UNION_SEPARATOR.join(
            [
                ENUM_VALUE_TEMPLATE.format(value="option1"),
                ENUM_VALUE_TEMPLATE.format(value="option2"),
            ]
        )
        assert result == expected

    def test_union_separator(self):
        """Test that union separator is used correctly."""
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        result = json_schema_to_schellma(schema)
        expected = TS_UNION_SEPARATOR.join(
            [TS_TYPE_MAPPINGS["string"], TS_TYPE_MAPPINGS["integer"]]
        )
        assert result == expected

    def test_nullable_type(self):
        """Test that null type constant is used correctly."""
        schema = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        result = json_schema_to_schellma(schema)
        expected = f"{TS_TYPE_MAPPINGS['string']}{TS_UNION_SEPARATOR}{TS_NULL_TYPE}"
        assert result == expected

    def test_index_signature_any(self):
        """Test that index signature any is used correctly."""
        schema = {"type": "object", "additionalProperties": True}
        result = json_schema_to_schellma(schema)
        assert result == TS_INDEX_SIGNATURE_ANY

    def test_any_type_fallback(self):
        """Test that any type is used as fallback."""
        schema = {"type": "unknown"}
        result = json_schema_to_schellma(schema)
        assert result == TS_ANY_TYPE

    def test_defs_prefix_constant(self):
        """Test that DEFS_PREFIX constant is used correctly."""
        schema = {
            "type": "object",
            "properties": {"ref_field": {"$ref": f"{DEFS_PREFIX}TestType"}},
            "$defs": {
                "TestType": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                }
            },
        }
        result = json_schema_to_schellma(schema, define_types=True)
        assert "TestType" in result
        assert TS_TYPE_MAPPINGS["string"] in result

    def test_object_formatting_constants(self):
        """Test that object formatting constants are used correctly."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "A name field"},
                "age": {"type": "integer"},
            },
        }
        result = json_schema_to_schellma(schema)

        # Check that the result contains properly formatted object
        assert "{" in result
        assert "}" in result
        assert '"name": string,' in result
        assert '"age": int,' in result
        assert "// A name field" in result

    def test_constants_maintain_functionality(self):
        """Test that using constants maintains all functionality."""
        # Complex schema to test multiple constants
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "status": {"type": "string", "enum": ["active", "inactive"]},
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "optional": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
        }

        result = json_schema_to_schellma(schema)

        # Verify all expected parts are present with constants
        assert '"id": int,' in result
        assert '"tags": string[],' in result
        assert '"status": "active" | "inactive",' in result
        assert '"metadata": { [key: string]: string },' in result
        assert '"optional": string | null,' in result
