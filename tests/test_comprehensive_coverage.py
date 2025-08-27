"""Comprehensive tests for edge cases and full coverage."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from schellma import json_schema_to_typescript, pydantic_to_typescript_type


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class ComplexModel(BaseModel):
    """Model with complex nested structures for comprehensive testing."""

    # Basic types
    name: str = Field(description="The name field")
    age: int
    height: float
    is_active: bool

    # Optional and nullable
    nickname: str | None = None
    middle_name: str | None = None

    # Collections
    tags: list[str]
    scores: set[int]
    metadata: dict[str, Any]
    coordinates: tuple[float, float]

    # Enums
    favorite_color: Color

    # Complex nested
    nested_dict: dict[str, list[dict[str, str]]]


class TestComprehensiveCoverage:
    """Test comprehensive coverage of all functionality."""

    def test_complex_model_conversion(self):
        """Test conversion of complex model with all types."""
        result = pydantic_to_typescript_type(ComplexModel, define_types=True)

        # Check basic types
        assert '"name": string,' in result
        assert '"age": int,' in result
        assert '"height": number,' in result
        assert '"is_active": boolean,' in result

        # Check optional types
        assert '"nickname": string | null,' in result
        assert '"middle_name": string | null,' in result

        # Check collections
        assert '"tags": string[],' in result
        assert '"scores": int[],' in result
        assert '"metadata": { [key: string]: any },' in result
        assert '"coordinates": [number, number],' in result

        # Check enum (it shows as Color reference, not expanded)
        assert '"favorite_color": Color,' in result

        # Check complex nested
        assert (
            '"nested_dict": { [key: string]: { [key: string]: string }[] },' in result
        )

        # Check description comment
        assert "// The name field" in result

    def test_inline_vs_defined_types(self):
        """Test difference between inline and defined types."""
        inline_result = pydantic_to_typescript_type(ComplexModel, define_types=False)
        defined_result = pydantic_to_typescript_type(ComplexModel, define_types=True)

        # Inline should not have separate type definitions
        assert "Color {" not in inline_result

        # Defined should have Color reference
        assert '"favorite_color": Color,' in defined_result

    def test_edge_case_schemas(self):
        """Test edge case JSON schemas."""
        # Schema with no properties
        schema = {"type": "object"}
        result = json_schema_to_typescript(schema)
        assert result == "object"

        # Schema with empty properties
        empty_props_schema: dict[str, object] = {"type": "object", "properties": {}}
        result = json_schema_to_typescript(empty_props_schema)
        assert result == "{\n}"

        # Schema with only additionalProperties
        additional_props_schema: dict[str, object] = {
            "type": "object",
            "additionalProperties": True,
        }
        result = json_schema_to_typescript(additional_props_schema)
        assert result == "{ [key: string]: any }"

    def test_deeply_nested_structures(self):
        """Test deeply nested structures."""
        schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "deep_value": {"type": "string"}
                                        },
                                    },
                                }
                            },
                        }
                    },
                }
            },
        }

        result = json_schema_to_typescript(schema)
        assert '"level1": {' in result
        assert '"level2": {' in result
        assert '"level3": {' in result
        assert '"deep_value": string' in result

    def test_multiple_union_types(self):
        """Test complex union types."""
        schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"},
                {"type": "boolean"},
                {"type": "null"},
            ]
        }

        result = json_schema_to_typescript(schema)
        assert "string | int | boolean | null" in result

    def test_mixed_tuple_types(self):
        """Test tuples with mixed types."""
        schema = {
            "type": "array",
            "prefixItems": [
                {"type": "string"},
                {"type": "integer"},
                {"type": "boolean"},
                {"type": "number"},
                {"anyOf": [{"type": "string"}, {"type": "null"}]},
            ],
        }

        result = json_schema_to_typescript(schema)
        assert "[string, int, boolean, number, string | null]" in result

    def test_complex_additional_properties(self):
        """Test complex additionalProperties scenarios."""
        # additionalProperties with object type
        schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {"nested": {"type": "string"}},
            },
        }

        result = json_schema_to_typescript(schema)
        assert "{ [key: string]: {" in result
        assert '"nested": string' in result

    def test_enum_with_mixed_types(self):
        """Test enums with different value types."""
        schema = {"type": "string", "enum": ["active", "inactive", "pending"]}

        result = json_schema_to_typescript(schema)
        assert '"active" | "inactive" | "pending"' in result

    def test_all_primitive_types(self):
        """Test all supported primitive types."""
        primitives = {
            "string": "string",
            "integer": "int",
            "number": "number",
            "boolean": "boolean",
        }

        for json_type, ts_type in primitives.items():
            schema = {"type": json_type}
            result = json_schema_to_typescript(schema)
            assert result == ts_type

    def test_array_without_items(self):
        """Test array without items specification."""
        schema = {"type": "array"}
        result = json_schema_to_typescript(schema)
        assert result == "any[]"

    def test_object_with_description_only_properties(self):
        """Test object with properties that only have descriptions."""
        schema = {
            "type": "object",
            "properties": {
                "field1": {"type": "string", "description": "A string field"},
                "field2": {"type": "integer"},  # No description
                "field3": {"type": "boolean", "description": "A boolean field"},
            },
        }

        result = json_schema_to_typescript(schema)
        assert "// A string field" in result
        assert "// A boolean field" in result
        assert '"field1": string,' in result
        assert '"field2": int,' in result
        assert '"field3": boolean,' in result

    def test_oneOf_vs_anyOf(self):
        """Test difference between oneOf and anyOf (should be same output)."""
        any_of_schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}

        one_of_schema = {"oneOf": [{"type": "string"}, {"type": "integer"}]}

        any_of_result = json_schema_to_typescript(any_of_schema)
        one_of_result = json_schema_to_typescript(one_of_schema)

        # Both should produce the same union type
        assert any_of_result == one_of_result
        assert "string | int" in any_of_result

    def test_empty_enum(self):
        """Test enum with empty values list."""
        schema = {"type": "string", "enum": []}

        result = json_schema_to_typescript(schema)
        # Should return empty union (which becomes empty string when joined)
        assert result == ""

    def test_single_enum_value(self):
        """Test enum with single value."""
        schema = {"type": "string", "enum": ["only_value"]}

        result = json_schema_to_typescript(schema)
        assert result == '"only_value"'

    def test_model_with_field_constraints(self):
        """Test model with Pydantic field constraints."""

        class ConstrainedModel(BaseModel):
            name: str = Field(
                min_length=1, max_length=100, description="Name with constraints"
            )
            age: int = Field(ge=0, le=150, description="Age with range")
            email: str = Field(
                pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Email with pattern"
            )

        result = pydantic_to_typescript_type(ConstrainedModel)

        # Constraints should not affect TypeScript output, but descriptions should be present
        assert "// Name with constraints" in result
        assert "// Age with range" in result
        assert "// Email with pattern" in result
        assert '"name": string,' in result
        assert '"age": int,' in result
        assert '"email": string,' in result

    def test_recursive_model_structure(self):
        """Test model with recursive-like structure (but not circular)."""

        class TreeNode(BaseModel):
            value: str
            children: list["TreeNode"] = []

        # This should work without circular reference error
        result = pydantic_to_typescript_type(TreeNode, define_types=True)
        assert "TreeNode" in result
        assert '"value": string' in result
        assert '"children": TreeNode[]' in result

    def test_coverage_of_all_constants(self):
        """Test that all constants are used in various scenarios."""
        from schellma.constants import (
            TS_ANY_ARRAY_TYPE,
            TS_ANY_TYPE,
            TS_INDEX_SIGNATURE_ANY,
            TS_NULL_TYPE,
            TS_OBJECT_TYPE,
        )

        # Test any type fallback
        schema = {"type": "unknown"}
        result = json_schema_to_typescript(schema)
        assert result == TS_ANY_TYPE

        # Test null type in union
        null_union_schema: dict[str, object] = {"anyOf": [{"type": "null"}]}
        result = json_schema_to_typescript(null_union_schema)
        assert TS_NULL_TYPE in result

        # Test object type fallback
        object_schema = {"type": "object"}
        result = json_schema_to_typescript(object_schema)
        assert result == TS_OBJECT_TYPE

        # Test any array fallback
        array_schema = {"type": "array"}
        result = json_schema_to_typescript(array_schema)
        assert result == TS_ANY_ARRAY_TYPE

        # Test index signature any
        index_sig_schema: dict[str, object] = {
            "type": "object",
            "additionalProperties": True,
        }
        result = json_schema_to_typescript(index_sig_schema)
        assert result == TS_INDEX_SIGNATURE_ANY
