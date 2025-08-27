"""Test type annotations compatibility."""

import sys
from typing import get_type_hints

from schellma.converters import pydantic_to_typescript_type
from schellma.models import NestedModel


def test_python_version_compatibility():
    """Test that we're running on Python 3.11+."""
    assert sys.version_info >= (3, 11), "Package requires Python 3.11+"


def test_type_annotations():
    """Test that type annotations are properly defined."""
    hints = get_type_hints(pydantic_to_typescript_type)

    # Check that model_class parameter has correct type annotation
    assert "model_class" in hints
    assert "define_types" in hints
    assert "return" in hints

    # Verify return type is str
    assert hints["return"] is str


def test_function_signature():
    """Test that the function signature works with type[BaseModel]."""
    # This should not raise any type errors
    result = pydantic_to_typescript_type(NestedModel, define_types=True)
    assert isinstance(result, str)
    assert len(result) > 0
