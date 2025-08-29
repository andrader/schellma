"""Test indentation functionality."""

from pydantic import BaseModel, Field

from schellma import json_schema_to_schellma, pydantic_to_schellma


class SimpleModel(BaseModel):
    """Simple model for testing indentation."""

    name: str = Field(description="The name field")
    age: int


class TestIndentation:
    """Test indentation configuration."""

    def test_default_indentation(self):
        """Test default indentation (2 spaces)."""
        result = pydantic_to_schellma(SimpleModel)

        # Should use 2 spaces for properties
        assert '  "name": string,' in result
        assert '  "age": int,' in result
        assert "  // The name field" in result
        assert result.endswith("}")

    def test_custom_indentation_4_spaces(self):
        """Test custom indentation with 4 spaces."""
        result = pydantic_to_schellma(SimpleModel, indent=4)

        # Should use 4 spaces for properties
        assert '    "name": string,' in result
        assert '    "age": int,' in result
        assert "    // The name field" in result
        assert result.endswith("}")

    def test_no_indentation(self):
        """Test no indentation (compact format)."""
        result = pydantic_to_schellma(SimpleModel, indent=False)

        # Should have no indentation
        assert '"name": string,' in result
        assert '"age": int,' in result
        # Comments should also have no indentation
        assert "// The name field" in result
        assert result.endswith("}")

    def test_no_indentation_with_none(self):
        """Test no indentation using None."""
        result = pydantic_to_schellma(SimpleModel, indent=None)

        # Should have no indentation
        assert '"name": string,' in result
        assert '"age": int,' in result
        assert result.endswith("}")

    def test_no_indentation_with_zero(self):
        """Test no indentation using 0."""
        result = pydantic_to_schellma(SimpleModel, indent=0)

        # Should have no indentation
        assert '"name": string,' in result
        assert '"age": int,' in result
        assert result.endswith("}")

    def test_json_schema_indentation(self):
        """Test indentation with direct JSON schema conversion."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "A name field"},
                "value": {"type": "integer"},
            },
        }

        # Test with 3 spaces
        result = json_schema_to_schellma(schema, indent=3)
        assert '   "name": string,' in result
        assert '   "value": int,' in result
        assert "   // A name field" in result

    def test_nested_objects_indentation(self):
        """Test indentation with nested objects."""

        class Address(BaseModel):
            street: str
            city: str

        class User(BaseModel):
            name: str
            address: Address

        result = pydantic_to_schellma(User, define_types=True, indent=2)

        # Both the Address definition and main object should use same indentation
        assert '  "street": string,' in result
        assert '  "city": string,' in result
        assert '  "name": string,' in result
        assert '  "address": Address,' in result

    def test_compact_vs_indented_comparison(self):
        """Test difference between compact and indented formats."""
        compact = pydantic_to_schellma(SimpleModel, indent=False)
        indented = pydantic_to_schellma(SimpleModel, indent=2)

        # Compact should be shorter (due to less whitespace)
        assert len(compact) < len(indented)

        # Both should have same content, just different formatting
        compact_lines = [line.strip() for line in compact.split("\n") if line.strip()]
        indented_lines = [line.strip() for line in indented.split("\n") if line.strip()]

        # Remove comment lines for comparison (they have same content but different indentation)
        compact_content = [
            line for line in compact_lines if not line.strip().startswith("//")
        ]
        indented_content = [
            line for line in indented_lines if not line.strip().startswith("//")
        ]

        assert compact_content == indented_content

        # Verify both have the same comment content (just different indentation)
        compact_comments = [
            line.strip() for line in compact_lines if line.strip().startswith("//")
        ]
        indented_comments = [
            line.strip() for line in indented_lines if line.strip().startswith("//")
        ]
        assert compact_comments == indented_comments

    def test_invalid_indent_uses_default(self):
        """Test that invalid indent values fall back to default."""
        # Negative numbers should use default
        result = pydantic_to_schellma(SimpleModel, indent=-1)
        assert '  "name": string,' in result  # Should use default 2 spaces

        # String should use default (though type system should prevent this)
        # This tests the runtime behavior if someone bypasses type checking
