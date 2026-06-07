import pytest
import pandas as pd
from core.excel_loader import load_excel

def test_load_excel_basic(tmp_path):
    excel_path = tmp_path / "master.xlsx"
    
    # Create a simple dataframe
    df = pd.DataFrame({
        "placas": ["AB123CD", "EF456GH", " IJ789KL "],
        "Owner": ["Alice", "Bob", "Charlie"]
    })
    df.to_excel(excel_path, index=False)
    
    # Load basic
    res = load_excel(str(excel_path), ignore_ext=False, ignore_case=False, preprocess=False)
    assert len(res) == 3
    # Check key trimming
    assert "AB123CD" in res
    assert "EF456GH" in res
    assert "IJ789KL" in res # spaces trimmed
    
    # Check value details preserved
    assert res["AB123CD"]["Owner"] == "Alice"
    assert res["EF456GH"]["placas"] == "EF456GH"

def test_load_excel_unnamed_handling(tmp_path):
    excel_path = tmp_path / "unnamed.xlsx"
    
    # Create dataframe with unnamed columns (empty headers)
    df = pd.DataFrame([
        ["AB123CD", "Extra Info 1", "Extra Info 2"],
        ["EF456GH", "More Info 1", "More Info 2"]
    ], columns=["placas", "", "Unnamed: 2"])
    
    # pandas will read the empty column header as Unnamed: 1
    df.to_excel(excel_path, index=False)
    
    res = load_excel(str(excel_path))
    assert len(res) == 2
    
    # The columns should be renamed to Info and Info_2
    row = res["AB123CD"]
    assert "Info" in row
    assert "Info_2" in row
    assert row["Info"] == "Extra Info 1"
    assert row["Info_2"] == "Extra Info 2"

def test_load_excel_special_processing(tmp_path):
    excel_path = tmp_path / "special.xlsx"
    
    df = pd.DataFrame({
        "Placa": ["ABC-123.pdf", "xyz_456.docx", "ABC-123.pdf"], # Duplicates after cleaning
        "Detail": ["D1", "D2", "D3"]
    })
    df.to_excel(excel_path, index=False)
    
    # ignore_ext=True, preprocess=True, ignore_case=True
    res = load_excel(str(excel_path), ignore_ext=True, ignore_case=True, preprocess=True)
    # ABC-123.pdf -> ABC-123 (ext) -> abc (preprocess + lowercase)
    # xyz_456.docx -> xyz_456 (ext) -> xyz (preprocess + lowercase)
    # Duplicate 'abc' should be dropped (keeping first)
    assert len(res) == 2
    assert "abc" in res
    assert "xyz" in res
    assert res["abc"]["Detail"] == "D1"

def test_load_csv(tmp_path):
    csv_path = tmp_path / "data.csv"
    
    # Create a CSV with semicolon separator
    csv_content = "placas;Owner;Detail\nAB123CD;Alice;D1\nEF456GH;Bob;D2"
    csv_path.write_text(csv_content, encoding="utf-8")
    
    res = load_excel(str(csv_path))
    assert len(res) == 2
    assert "AB123CD" in res
    assert "EF456GH" in res
    assert res["AB123CD"]["Owner"] == "Alice"
    assert res["EF456GH"]["Detail"] == "D2"

def test_load_json(tmp_path):
    json_path = tmp_path / "data.json"
    
    # Create a JSON list of objects
    json_content = '[{"placas": "AB123CD", "Owner": "Alice"}, {"placas": "EF456GH", "Owner": "Bob"}]'
    json_path.write_text(json_content, encoding="utf-8")
    
    res = load_excel(str(json_path))
    assert len(res) == 2
    assert "AB123CD" in res
    assert "EF456GH" in res
    assert res["AB123CD"]["Owner"] == "Alice"

