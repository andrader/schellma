#!/usr/bin/env python3
"""Comprehensive tests for advanced array types (contains, minContains/maxContains, tuples)."""

from schellma import json_schema_to_llm


class TestAdvancedArrays:
    """Test advanced array type handling."""

    def test_contains_string_pattern(self):
        """Test contains constraint with string pattern."""
        schema = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "contains": {"type": "string", "pattern": "^required_"},
                    "description": "Tags array with required prefix",
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show contains constraint with pattern description
        assert "contains: string starting with 'required_'" in result
        assert "Tags array with required prefix" in result
        assert "string[]" in result

    def test_contains_with_min_max(self):
        """Test contains with minContains and maxContains."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "contains": {"type": "string", "pattern": "^tag:"},
                    "minContains": 1,
                    "maxContains": 3,
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show both contains pattern and count constraints
        assert "contains: string starting with 'tag:'" in result
        assert "contains: 1-3 items" in result

    def test_contains_enum_values(self):
        """Test contains constraint with enum values."""
        schema = {
            "type": "object",
            "properties": {
                "statuses": {
                    "type": "array",
                    "contains": {"enum": ["active", "pending"]},
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show contains with enum options
        assert 'contains: one of "active", "pending"' in result

    def test_contains_const_value(self):
        """Test contains constraint with const value."""
        schema = {
            "type": "object",
            "properties": {
                "flags": {"type": "array", "contains": {"const": "required"}}
            },
        }

        result = json_schema_to_llm(schema)

        # Should show contains with const value
        assert 'contains: "required"' in result

    def test_contains_only_array(self):
        """Test array with only contains constraint (no items)."""
        schema = {
            "type": "object",
            "properties": {"mixed": {"type": "array", "contains": {"type": "number"}}},
        }

        result = json_schema_to_llm(schema)

        # Should infer type from contains
        assert "number[]" in result
        assert "contains: number" in result

    def test_min_contains_only(self):
        """Test minContains without maxContains."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "contains": {"type": "string"},
                    "minContains": 2,
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show minContains constraint
        assert "minContains: 2" in result

    def test_max_contains_only(self):
        """Test maxContains without minContains."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "contains": {"type": "string"},
                    "maxContains": 5,
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show maxContains constraint
        assert "maxContains: 5" in result

    def test_tuple_with_additional_items(self):
        """Test tuple with additional items allowed."""
        schema = {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "number", "description": "latitude"},
                        {"type": "number", "description": "longitude"},
                    ],
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 4,
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show tuple with spread syntax for additional items
        assert "[number, number, ...number[]]" in result
        assert "items: 2-4" in result

    def test_tuple_without_additional_items(self):
        """Test strict tuple without additional items."""
        schema = {
            "type": "object",
            "properties": {
                "point": {
                    "type": "array",
                    "prefixItems": [{"type": "number"}, {"type": "number"}],
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show strict tuple
        assert "[number, number]" in result
        # Should not have spread syntax
        assert "..." not in result

    def test_complex_contains_pattern(self):
        """Test contains with complex pattern matching."""
        schema = {
            "type": "object",
            "properties": {
                "emails": {
                    "type": "array",
                    "contains": {
                        "type": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    },
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show contains with pattern (fallback to showing pattern)
        assert "contains: string matching pattern" in result

    def test_array_with_all_constraints(self):
        """Test array with multiple constraint types."""
        schema = {
            "type": "object",
            "properties": {
                "complex_array": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10,
                    "uniqueItems": True,
                    "contains": {"type": "string", "pattern": "^required_"},
                    "minContains": 1,
                    "maxContains": 2,
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should show all constraints
        assert "items: 1-10" in result
        assert "uniqueItems: true" in result
        assert "contains: string starting with 'required_'" in result
        assert "contains: 1-2 items" in result

    def test_contains_constraint_error_handling(self):
        """Test contains constraint with invalid schema."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "contains": "invalid",  # Invalid contains schema
                }
            },
        }

        result = json_schema_to_llm(schema)

        # Should fallback gracefully
        assert "any[]" in result
