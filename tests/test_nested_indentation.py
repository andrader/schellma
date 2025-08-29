"""Test nested indentation levels."""

from pydantic import BaseModel

from schellma import pydantic_to_schellma


class Address(BaseModel):
    street: str
    city: str
    country: str


class User(BaseModel):
    name: str
    age: int
    addresses: list[Address]


class TestNestedIndentation:
    """Test indentation for nested objects."""

    def test_nested_object_indentation_inline(self):
        """Test that nested objects have proper cumulative indentation when define_types=False."""
        result = pydantic_to_schellma(User, define_types=False, indent=2)

        print("Result:")
        print(result)

        # Level 1 properties should have 2 spaces
        assert '  "name": string,' in result
        assert '  "age": int,' in result

        # The addresses array should be at level 1 (2 spaces)
        assert '  "addresses": {' in result

        # Nested object properties should be at level 2 (4 spaces)
        assert '    "street": string,' in result
        assert '    "city": string,' in result
        assert '    "country": string,' in result

        # Closing brace for nested object should be at level 1 (2 spaces)
        assert "  }[]," in result

    def test_deeply_nested_indentation(self):
        """Test indentation for deeply nested structures."""
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
                                    "type": "object",
                                    "properties": {"deep_value": {"type": "string"}},
                                }
                            },
                        }
                    },
                }
            },
        }

        from schellma import json_schema_to_schellma

        result = json_schema_to_schellma(schema, define_types=False, indent=2)

        print("Deep nested result:")
        print(result)

        # Level 1: 2 spaces
        assert '  "level1": {' in result

        # Level 2: 4 spaces
        assert '    "level2": {' in result

        # Level 3: 6 spaces
        assert '      "level3": {' in result

        # Level 4: 8 spaces
        assert '        "deep_value": string,' in result

    def test_nested_vs_defined_types(self):
        """Test that define_types=True doesn't have this issue."""
        result_defined = pydantic_to_schellma(User, define_types=True, indent=2)
        result_inline = pydantic_to_schellma(User, define_types=False, indent=2)

        print("Defined types result:")
        print(result_defined)
        print("\nInline result:")
        print(result_inline)

        # With define_types=True, we should see Address as a reference
        assert '"addresses": Address[],' in result_defined

        # With define_types=False, we should see inline object with proper indentation
        assert '  "addresses": {' in result_inline
        assert '    "street": string,' in result_inline
