"""Test module structure and imports."""

from schellma import (
    json_schema_to_llm,
    pydantic_to_llm,
)
from schellma.converters import json_schema_to_llm as ConvertersFunction
from schellma.examples import ComprehensiveTest
from schellma.models import NestedModel, Status


def test_main_imports():
    """Test that main package imports work correctly."""
    assert callable(json_schema_to_llm)
    assert callable(pydantic_to_llm)


def test_converters_module():
    """Test that converters module exports work correctly."""
    assert callable(ConvertersFunction)
    assert ConvertersFunction is json_schema_to_llm


def test_examples_module():
    """Test that examples module works correctly."""
    assert ComprehensiveTest is not None
    # Test that ComprehensiveTest can be instantiated (basic structure test)
    from datetime import date, datetime, time
    from decimal import Decimal
    from uuid import uuid4

    instance = ComprehensiveTest(
        text="test",
        number=42,
        decimal_val=Decimal("10.5"),
        is_active=True,
        created_at=datetime.now(),
        birth_date=date.today(),
        meeting_time=time(10, 30),
        user_id=uuid4(),
        tags=["tag1", "tag2"],
        scores={1, 2, 3},
        metadata={"key": "value"},
        coordinates=(1.0, 2.0),
        variable_tuple=("a", "b", "c"),
        optional_text=None,
        optional_nested=None,
        nested_dict={"key": []},
        tuple_with_models=(
            NestedModel(text="test1", number=1),
            NestedModel(text="test2", number=2),
        ),
        status=Status.ACTIVE,
    )
    assert instance.text == "test"
    assert instance.status == Status.ACTIVE


def test_basic_conversion():
    """Test basic conversion functionality works after module restructure."""
    result = pydantic_to_llm(NestedModel, define_types=False)
    assert "string" in result
    assert "int" in result
