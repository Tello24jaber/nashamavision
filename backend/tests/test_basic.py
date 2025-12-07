"""
Simple working test to verify test infrastructure
"""
import pytest


def test_basic_math():
    """Test that basic Python works"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Test string operations"""
    text = "Nashama Vision"
    assert "Nashama" in text
    assert len(text) > 0


def test_list_operations():
    """Test list operations"""
    items = [1, 2, 3, 4, 5]
    assert len(items) == 5
    assert sum(items) == 15
    assert max(items) == 5


@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (10, -5, 5),
])
def test_addition_parametrized(a, b, expected):
    """Test addition with multiple parameters"""
    assert a + b == expected


def test_dictoperations():
    """Test dictionary operations"""
    data = {"name": "test", "value": 42}
    assert data["name"] == "test"
    assert data.get("value") == 42
    assert "name" in data
