#!/usr/bin/env python
"""Unit tests for kmos.io utility functions."""

import io as stdio

import pytest


def test_flatten():
    """Test _flatten function flattens nested lists."""
    from kmos.io import _flatten

    # Test empty list
    assert _flatten([]) == []

    # Test single list
    assert _flatten([[1, 2, 3]]) == [1, 2, 3]

    # Test multiple lists
    assert _flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]

    # Test mixed types
    assert _flatten([["a", "b"], ["c"]]) == ["a", "b", "c"]

    # Test empty sublists
    assert _flatten([[], [1, 2], []]) == [1, 2]


def test_chop_line():
    """Test _chop_line function splits long lines at commas."""
    from kmos.io import _chop_line

    # Test short line (no chopping needed)
    short = "short line"
    assert _chop_line(short) == short

    # Test line exactly at length
    line = "a" * 99
    assert _chop_line(line, line_length=100) == line

    # Test long line with commas
    # The function finds the next comma AFTER line_length and breaks there
    long_line = "a" * 50 + "," + "b" * 60
    result = _chop_line(long_line, line_length=100)
    assert "&\n" in result
    assert result.endswith("&\n")
    # Verify it was split
    parts = result.split("&\n")
    assert len(parts) > 1

    # Test line with multiple commas - breaks at comma after line_length
    multi_comma = ", ".join(["x" * 30 for _ in range(10)])
    result = _chop_line(multi_comma, line_length=100)
    # Should have multiple parts
    parts = [p for p in result.split("&\n") if p]
    assert len(parts) > 1
    # Each part should end with comma (except possibly last)
    for part in parts[:-1]:
        assert part.strip().endswith(",")

    # Test line without commas after line_length
    no_comma = "a" * 150
    result = _chop_line(no_comma, line_length=100)
    # Should return whole line with &\n at end
    assert result == no_comma + "&\n"


def test_most_common():
    """Test _most_common function finds most frequent element."""
    from kmos.io import _most_common

    # Test simple list
    assert _most_common([1, 2, 2, 3]) == 2

    # Test tie - should return earliest
    assert _most_common([1, 2, 1, 2]) == 1

    # Test strings
    assert _most_common(["a", "b", "b", "c"]) == "b"

    # Test single element
    assert _most_common([1]) == 1

    # Test all different (should return first)
    assert _most_common([1, 2, 3, 4]) == 1

    # Test frequency tie but different positions
    assert _most_common([1, 2, 3, 1, 2]) == 1  # 1 appears first


def test_print_dict(capsys):
    """Test _print_dict function prints nested dictionaries."""
    from kmos.io import _print_dict

    # Test simple dict
    simple = {"key1": "value1", "key2": "value2"}
    _print_dict(simple)
    captured = capsys.readouterr()
    assert "key1 = value1" in captured.out
    assert "key2 = value2" in captured.out

    # Test nested dict
    nested = {"outer": {"inner": "value"}}
    _print_dict(nested)
    captured = capsys.readouterr()
    assert "outer:" in captured.out
    assert "    inner = value" in captured.out

    # Test with custom indent
    _print_dict({"key": "value"}, indent="  ")
    captured = capsys.readouterr()
    assert "  key = value" in captured.out


def test_casetree_dict():
    """Test _casetree_dict function generates conditional assignments."""
    from kmos.io import _casetree_dict

    # Create a string buffer to capture output
    out = stdio.StringIO()

    # Test simple dictionary with non-dict values
    # These are output as "key = value; return" statements
    simple = {1: "case_1", 2: "case_2"}
    _casetree_dict(simple, indent="  ", out=out)
    output = out.getvalue()

    # Should contain assignment statements
    assert "1 = case_1; return" in output
    assert "2 = case_2; return" in output

    # Test nested dictionary (creates Fortran case structure)
    out = stdio.StringIO()
    # String keys with dict values create case() statements
    nested = {
        "species1": {"state1": "action1", "state2": "action2"},
        "default": {"state3": "action3"},
    }
    _casetree_dict(nested, indent="  ", out=out)
    output = out.getvalue()

    # Should have case structure for nested dicts
    assert "case(species1)" in output
    assert "state1 = action1; return" in output
    assert "state2 = action2; return" in output
    # Default with nested dict creates "case default"
    assert "case default" in output
    assert "state3 = action3; return" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
