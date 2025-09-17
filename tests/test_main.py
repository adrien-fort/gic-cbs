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
        "Die Hard 2 16 45",  # valid
        "3"                  # exit menu
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert captured.out.count("Invalid input. Please try again.") == 2
    assert "Welcome to the GIC CBS application!" in captured.out
    assert "Welcome to GIC Cinemas" in captured.out
    assert "Thank you for using GIC Cinemas system.Bye!" in captured.out

def test_main_valid_first_try(capsys):
    from src import main as main_module
    user_inputs = ["Inception 8 10", "3"]  # valid movie input, then exit
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Invalid input. Please try again." not in captured.out
    assert "Welcome to the GIC CBS application!" in captured.out
    assert "Welcome to GIC Cinemas" in captured.out
    assert "Thank you for using GIC Cinemas system.Bye!" in captured.out

def test_main_menu_exit(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 8 10",  # valid movie input
        "3"                # exit immediately
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Thank you for using GIC Cinemas system.Bye!" in captured.out
    assert "Welcome to GIC Cinemas" in captured.out
    assert "seats available" in captured.out

def test_main_menu_invalid_then_exit(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 8 10",  # valid movie input
        "0",               # invalid menu selection
        "3"                # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Invalid selection. Please try again." in captured.out
    assert "Thank you for using GIC Cinemas system.Bye!" in captured.out

def test_main_menu_book_and_check(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 8 10",  # valid movie input
        "1",               # book tickets
        "2",               # check bookings
        "3"                # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Booking tickets - feature not yet implemented." in captured.out
    assert "Checking bookings - feature not yet implemented." in captured.out
    assert "Thank you for using GIC Cinemas system.Bye!" in captured.out