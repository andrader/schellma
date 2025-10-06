"""Test TypeAdapter support for non-BaseModel types."""

import pytest
from pydantic import BaseModel, Field

from schellma.converters import pydantic_to_schellma
from schellma.exceptions import InvalidSchemaError


class SimpleModel(BaseModel):
    """Simple model for union testing."""

    name: str
    value: int


class TestUnionTypes:
    """Test TypeAdapter with union types."""

    def test_union_of_primitives(self):
        """Test union of primitive types (str | int)."""
        union_type = str | int
        result = pydantic_to_schellma(union_type)
        assert "string | int" in result

    def test_union_of_str_and_none(self):
        """Test optional type (str | None)."""
        union_type = str | None
        result = pydantic_to_schellma(union_type)
        assert "string | null" in result

    def test_union_of_multiple_primitives(self):
        """Test union of multiple primitives (str | int | float | bool)."""
        union_type = str | int | float | bool
        result = pydantic_to_schellma(union_type)
        assert "string" in result
        assert "int" in result
        assert "number" in result  # float becomes number in JSON Schema
        assert "boolean" in result

    def test_union_with_list(self):
        """Test union with list type (str | list[int])."""
        union_type = str | list[int]
        result = pydantic_to_schellma(union_type)
        assert "string" in result
        assert "int[]" in result

    def test_union_with_dict(self):
        """Test union with dict type (str | dict[str, int])."""
        union_type = str | dict[str, int]
        result = pydantic_to_schellma(union_type)
        assert "string" in result
        # Should contain index signature or object type
        assert "int" in result

    def test_union_of_models(self):
        """Test union of BaseModel types."""

        class ModelA(BaseModel):
            field_a: str

        class ModelB(BaseModel):
            field_b: int

        union_type = ModelA | ModelB
        result = pydantic_to_schellma(union_type)
        # Both model structures should be present
        assert "field_a" in result
        assert "field_b" in result


class TestListTypes:
    """Test TypeAdapter with list types."""

    def test_list_of_strings(self):
        """Test simple list of strings."""
        list_type = list[str]
        result = pydantic_to_schellma(list_type)
        assert "string[]" in result

    def test_list_of_integers(self):
        """Test simple list of integers."""
        list_type = list[int]
        result = pydantic_to_schellma(list_type)
        assert "int[]" in result

    def test_list_of_models(self):
        """Test list of BaseModel instances."""
        list_type = list[SimpleModel]
        result = pydantic_to_schellma(list_type)
        assert "name" in result
        assert "value" in result
        assert "[]" in result

    def test_nested_lists(self):
        """Test nested list types (list[list[int]])."""
        list_type = list[list[int]]
        result = pydantic_to_schellma(list_type)
        assert "int[][]" in result or "int[" in result


class TestDictTypes:
    """Test TypeAdapter with dict types."""

    def test_dict_str_int(self):
        """Test dict with string keys and int values."""
        dict_type = dict[str, int]
        result = pydantic_to_schellma(dict_type)
        assert "int" in result
        # Should have index signature format
        assert "{" in result

    def test_dict_str_any(self):
        """Test dict with string keys and Any values."""
        from typing import Any

        dict_type = dict[str, Any]
        result = pydantic_to_schellma(dict_type)
        assert "any" in result

    def test_dict_with_model_values(self):
        """Test dict with model values."""
        dict_type = dict[str, SimpleModel]
        result = pydantic_to_schellma(dict_type)
        assert "name" in result
        assert "value" in result


class TestTupleTypes:
    """Test TypeAdapter with tuple types."""

    def test_tuple_fixed_size(self):
        """Test fixed-size tuple (tuple[str, int, bool])."""
        tuple_type = tuple[str, int, bool]
        result = pydantic_to_schellma(tuple_type)
        assert "string" in result
        assert "int" in result
        assert "boolean" in result

    def test_tuple_variable_length(self):
        """Test variable-length tuple (tuple[str, ...])."""
        tuple_type = tuple[str, ...]
        result = pydantic_to_schellma(tuple_type)
        assert "string" in result
        assert "[]" in result  # Should be array-like

    def test_tuple_of_models(self):
        """Test tuple containing models."""
        tuple_type = tuple[SimpleModel, SimpleModel]
        result = pydantic_to_schellma(tuple_type)
        assert "name" in result
        assert "value" in result


class TestSetTypes:
    """Test TypeAdapter with set types."""

    def test_set_of_strings(self):
        """Test set of strings."""
        set_type = set[str]
        result = pydantic_to_schellma(set_type)
        # Sets are typically converted to arrays
        assert "string" in result

    def test_set_of_integers(self):
        """Test set of integers."""
        set_type = set[int]
        result = pydantic_to_schellma(set_type)
        assert "int" in result


class TestComplexNestedTypes:
    """Test TypeAdapter with complex nested type combinations."""

    def test_list_of_unions(self):
        """Test list of union types (list[str | int])."""
        complex_type = list[str | int]
        result = pydantic_to_schellma(complex_type)
        assert "string" in result
        assert "int" in result

    def test_dict_with_union_values(self):
        """Test dict with union values (dict[str, str | int | None])."""
        complex_type = dict[str, str | int | None]
        result = pydantic_to_schellma(complex_type)
        assert "string" in result
        assert "int" in result
        assert "null" in result

    def test_optional_list(self):
        """Test optional list type (list[str] | None)."""
        complex_type = list[str] | None
        result = pydantic_to_schellma(complex_type)
        assert "string" in result
        assert "null" in result

    def test_nested_dict_structure(self):
        """Test nested dict structure (dict[str, dict[str, int]])."""
        complex_type = dict[str, dict[str, int]]
        result = pydantic_to_schellma(complex_type)
        assert "int" in result


class TestPrimitiveTypes:
    """Test TypeAdapter with primitive types."""

    def test_str_type(self):
        """Test simple str type."""
        result = pydantic_to_schellma(str)
        assert "string" in result

    def test_int_type(self):
        """Test simple int type."""
        result = pydantic_to_schellma(int)
        assert "int" in result

    def test_float_type(self):
        """Test simple float type."""
        result = pydantic_to_schellma(float)
        assert "number" in result  # float becomes number in JSON Schema

    def test_bool_type(self):
        """Test simple bool type."""
        result = pydantic_to_schellma(bool)
        assert "boolean" in result


class TestTypeAdapterEdgeCases:
    """Test edge cases and error handling for TypeAdapter."""

    def test_invalid_type_still_raises_error(self):
        """Test that truly invalid types still raise errors."""
        # Pass a non-type object (not a class or type)
        with pytest.raises(InvalidSchemaError):
            pydantic_to_schellma("not a type")  # type: ignore

    def test_none_type_conversion(self):
        """Test that None type can be converted via TypeAdapter."""
        # TypeAdapter converts type(None) to any type
        result = pydantic_to_schellma(type(None))
        assert "any" in result

    def test_type_adapter_with_define_types(self):
        """Test that TypeAdapter works with define_types=True."""
        union_type = str | int | None
        result = pydantic_to_schellma(union_type, define_types=True)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_type_adapter_with_custom_indent(self):
        """Test that TypeAdapter works with custom indentation."""
        union_type = dict[str, str | int]
        result = pydantic_to_schellma(union_type, indent=4)
        assert isinstance(result, str)
        assert len(result) > 0


class TestTypeAdapterWithConstraints:
    """Test TypeAdapter with Pydantic constraints."""

    def test_annotated_str_with_constraints(self):
        """Test annotated string with constraints."""
        from typing import Annotated

        constrained_type = Annotated[str, Field(min_length=3, max_length=10)]
        result = pydantic_to_schellma(constrained_type)
        assert "string" in result
        # Note: Constraints might be in comments depending on implementation
        # The test just verifies it doesn't crash

    def test_annotated_int_with_constraints(self):
        """Test annotated int with constraints."""
        from typing import Annotated

        constrained_type = Annotated[int, Field(ge=0, le=100)]
        result = pydantic_to_schellma(constrained_type)
        assert "int" in result

    def test_list_with_constraints(self):
        """Test list with item constraints."""
        from typing import Annotated

        constrained_type = list[Annotated[str, Field(min_length=1)]]
        result = pydantic_to_schellma(constrained_type)
        assert "string" in result
        assert "[]" in result
