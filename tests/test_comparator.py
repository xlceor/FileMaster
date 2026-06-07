import pytest
from core.comparator import preprocess_placas, compare_files, compare_dicts

def test_preprocess_placas():
    assert preprocess_placas("1234ABC-extra") == "1234ABC"
    assert preprocess_placas("5678XYZ_other") == "5678XYZ"
    assert preprocess_placas("ABC-123_XYZ") == "ABC"
    assert preprocess_placas("simple") == "simple"
    assert preprocess_placas("   trimmedspace   ") == "trimmedspace"

def test_compare_files():
    expected = {"abc", "def", "ghi"}
    found_list = ["abc", "def", "jkl"]
    
    # Case sensitive
    res = compare_files(expected, found_list, ignore_case=False)
    assert res["found"] == {"abc", "def"}
    assert res["missing"] == {"ghi"}
    assert res["extra"] == {"jkl"}
    
    # Case insensitive
    expected_anycase = {"ABC", "def"}
    found_anycase = ["abc", "DEF", "GHI"]
    res_anycase = compare_files(expected_anycase, found_anycase, ignore_case=True)
    assert res_anycase["found"] == {"abc", "def"}
    assert res_anycase["missing"] == set()
    assert res_anycase["extra"] == {"ghi"}

def test_compare_dicts():
    master = {
        "1": {"name": "Alice", "role": "admin"},
        "2": {"name": "Bob", "role": "user"},
        "3": {"name": "Charlie", "role": "user"}
    }
    real = {
        "1": {"name": "Alice", "role": "admin"},
        "2": {"name": "Bob", "role": "user"},
        "4": {"name": "Dave", "role": "guest"}
    }
    
    found, missing, extra = compare_dicts(master, real)
    assert set(found.keys()) == {"1", "2"}
    assert set(missing.keys()) == {"3"}
    assert set(extra.keys()) == {"4"}
    
    assert found["1"]["name"] == "Alice"
    assert missing["3"]["name"] == "Charlie"
    assert extra["4"]["name"] == "Dave"
