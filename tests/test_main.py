import pytest
from unittest import mock
from src.main import main  # Updated import for src directory

def test_startup_prompt(capsys):
    with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
        try:
            main()
        except KeyboardInterrupt:
            pass  # Allow test to exit gracefully

    captured = capsys.readouterr()
    assert "Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:" in captured.out
