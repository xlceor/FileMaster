import pytest
from pathlib import Path
from core.scanner import scan_folder

def test_scan_folder_non_recursive(tmp_path):
    # Setup test folder structure
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.pdf").write_text("content")
    
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "file3.txt").write_text("content")
    
    # Non-recursive
    files = scan_folder(str(tmp_path), recursive=False, ignore_ext=False, preprocess=False)
    # subdir is a directory, so it should be ignored by is_file() check
    assert files == ["file1.txt", "file2.pdf"]

def test_scan_folder_recursive(tmp_path):
    (tmp_path / "file1.txt").write_text("content")
    
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "file2.txt").write_text("content")
    
    # Recursive
    files = scan_folder(str(tmp_path), recursive=True, ignore_ext=False, preprocess=False)
    assert files == ["file1.txt", "file2.txt"]

def test_scan_folder_ignore_ext(tmp_path):
    (tmp_path / "file1.tar.gz").write_text("content")
    (tmp_path / "file2.txt").write_text("content")
    
    files = scan_folder(str(tmp_path), recursive=False, ignore_ext=True, preprocess=False)
    # note: pathlib's stem for file1.tar.gz is file1.tar
    assert files == ["file1.tar", "file2"]

def test_scan_folder_preprocess(tmp_path):
    (tmp_path / "ABC-123.txt").write_text("content")
    (tmp_path / "XYZ_456.pdf").write_text("content")
    
    files = scan_folder(str(tmp_path), recursive=False, ignore_ext=False, preprocess=True)
    # Preprocess removes everything after - or _
    # ABC-123.txt becomes ABC
    # XYZ_456.pdf becomes XYZ
    assert files == ["ABC", "XYZ"]
