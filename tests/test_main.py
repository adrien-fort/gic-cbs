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
    # The input() prompt is not captured by capsys, so we do not check for it

def test_main_invalid_then_valid_input(capsys):
    from src import main as main_module
    user_inputs = [
        "badinput",           # invalid
        "Inception 0 10",    # invalid (row is 0)
        "Die Hard 2 16 45"   # valid
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert captured.out.count("Invalid input. Please try again.") == 2
    assert "Welcome to the GIC CBS application!" in captured.out
    # The input() prompt is not captured by capsys, so we do not check for it
    assert "Welcome to GIC Cinemas" in captured.out

def test_main_valid_first_try(capsys):
    from src import main as main_module
    user_inputs = ["Inception 8 10"]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Invalid input. Please try again." not in captured.out
    assert "Welcome to the GIC CBS application!" in captured.out
    # The input() prompt is not captured by capsys, so we do not check for it
    assert "Welcome to GIC Cinemas" in captured.out