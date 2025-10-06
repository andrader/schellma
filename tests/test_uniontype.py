"""Test UnionType support."""

from types import UnionType

from schellma import schellma


class TestUnionType:
    """Test UnionType handling in schellma function."""

    def test_simple_union(self):
        """Test simple UnionType with two types."""
        union_type = str | int
        result = schellma(union_type)
        assert "string | int" in result

    def test_complex_union(self):
        """Test complex UnionType with multiple types."""
        complex_union = str | int | list[str]
        result = schellma(complex_union)
        assert "string" in result
        assert "int" in result
        assert "string[]" in result

    def test_nullable_union(self):
        """Test UnionType with None."""
        nullable_union = str | None
        result = schellma(nullable_union)
        assert "string | null" in result

    def test_nested_union(self):
        """Test nested UnionType with complex types."""
        nested_union = dict[str, int] | list[str]
        result = schellma(nested_union)
        assert "string[]" in result
        # Check for index signature pattern
        assert "[key: string]: int" in result or "{ [key: string]: int }" in result

    def test_union_type_instance_check(self):
        """Test that UnionType is correctly identified."""
        union_type = str | int
        assert isinstance(union_type, UnionType)

    def test_union_with_bool(self):
        """Test UnionType with boolean."""
        union_type = str | bool
        result = schellma(union_type)
        assert "string" in result
        assert "boolean" in result

    def test_triple_union(self):
        """Test UnionType with three types."""
        triple_union = str | int | float
        result = schellma(triple_union)
        assert "string" in result
        assert "int" in result
        assert "number" in result
