#!/usr/bin/env python3
"""Comprehensive tests for advanced union types (allOf, not, discriminated unions)."""

from schellma import json_schema_to_schellma


class TestAdvancedUnions:
    """Test advanced union type handling."""

    def test_allof_intersection(self):
        """Test allOf intersection type conversion."""
        schema = {
            "type": "object",
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier"},
                        "created_at": {
                            "type": "string",
                            "description": "Creation timestamp",
                        },
                    },
                    "required": ["id", "created_at"],
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "User name"},
                        "email": {"type": "string", "description": "User email"},
                    },
                    "required": ["name", "email"],
                },
            ],
        }

        result = json_schema_to_schellma(schema)

        # Should merge all properties from both schemas
        assert '"id": string' in result
        assert '"created_at": string' in result
        assert '"name": string' in result
        assert '"email": string' in result

        # All fields should be marked as required
        assert "Unique identifier, required" in result
        assert "Creation timestamp, required" in result
        assert "User name, required" in result
        assert "User email, required" in result

    def test_allof_with_descriptions(self):
        """Test allOf with schema descriptions for intersection comment."""
        schema = {
            "type": "object",
            "allOf": [
                {
                    "type": "object",
                    "description": "Base entity fields",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                },
                {
                    "type": "object",
                    "description": "User-specific fields",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ],
        }

        result = json_schema_to_schellma(schema)

        # Should include intersection comment
        assert "Intersection of: Base entity fields, User-specific fields" in result

    def test_not_enum_constraint(self):
        """Test not constraint with enum exclusions."""
        schema = {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "not": {"enum": ["forbidden", "banned", "deleted"]},
                    "description": "Status excluding forbidden values",
                }
            },
        }

        result = json_schema_to_schellma(schema)

        # Should show not constraint with excluded values
        assert 'not: "forbidden", "banned", "deleted"' in result
        assert "Status excluding forbidden values" in result

    def test_not_single_value(self):
        """Test not constraint with single excluded value."""
        schema = {
            "type": "object",
            "properties": {"value": {"type": "string", "not": {"enum": ["admin"]}}},
        }

        result = json_schema_to_schellma(schema)

        # Should show single not constraint
        assert 'not: "admin"' in result

    def test_not_type_constraint(self):
        """Test not constraint with type exclusion."""
        schema = {"type": "object", "properties": {"value": {"not": {"type": "null"}}}}

        result = json_schema_to_schellma(schema)

        # Should show type exclusion
        assert "not: null" in result

    def test_discriminated_union_basic(self):
        """Test basic discriminated union handling."""
        schema = {
            "$defs": {
                "User": {
                    "type": "object",
                    "properties": {
                        "type": {"const": "user", "type": "string"},
                        "name": {"type": "string"},
                    },
                    "required": ["type", "name"],
                },
                "Admin": {
                    "type": "object",
                    "properties": {
                        "type": {"const": "admin", "type": "string"},
                        "permissions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["type", "permissions"],
                },
            },
            "type": "object",
            "properties": {
                "entity": {
                    "oneOf": [{"$ref": "#/$defs/User"}, {"$ref": "#/$defs/Admin"}],
                    "discriminator": {
                        "propertyName": "type",
                        "mapping": {"user": "#/$defs/User", "admin": "#/$defs/Admin"},
                    },
                }
            },
        }

        result = json_schema_to_schellma(schema)

        # Should show discriminator information
        assert 'type: "user"' in result
        assert 'type: "admin"' in result

    def test_complex_not_constraint(self):
        """Test complex not constraint with object pattern."""
        schema = {
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "not": {"properties": {"debug": {"const": True}}},
                }
            },
        }

        result = json_schema_to_schellma(schema)

        # Should show generic not constraint for complex patterns
        assert "not: specific object pattern" in result

    def test_allof_empty_schemas(self):
        """Test allOf with empty schemas."""
        schema = {"type": "object", "allOf": [{"type": "object"}, {"type": "object"}]}

        result = json_schema_to_schellma(schema)

        # Should handle empty allOf gracefully
        assert "{" in result
        assert "}" in result

    def test_nested_allof_constraints(self):
        """Test allOf with nested constraints and defaults."""
        schema = {
            "type": "object",
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 3,
                            "maxLength": 50,
                            "default": "Anonymous",
                        }
                    },
                    "required": ["name"],
                },
                {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    },
                },
            ],
        }

        result = json_schema_to_schellma(schema)

        # Should merge constraints and defaults
        assert 'default: "Anonymous"' in result
        assert "length: 3-50" in result
        assert "range: 0-150" in result
        assert "required" in result  # name should be required
        assert "optional" in result  # age should be optional
