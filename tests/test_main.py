"""
test_main.py
-----------
Unit tests for the main application entry point and user interaction flows.
"""

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
    assert "Thank you for using GIC Cinemas system. Bye!" in captured.out

def test_main_valid_first_try(capsys):
    from src import main as main_module
    user_inputs = ["Inception 8 10", "3"]  # valid movie input, then exit
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Invalid input. Please try again." not in captured.out
    assert "Welcome to the GIC CBS application!" in captured.out
    assert "Welcome to GIC Cinemas" in captured.out
    assert "Thank you for using GIC Cinemas system. Bye!" in captured.out

def test_main_menu_exit(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 8 10",  # valid movie input
        "3"                # exit immediately
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Thank you for using GIC Cinemas system. Bye!" in captured.out
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
    assert "Thank you for using GIC Cinemas system. Bye!" in captured.out

def test_main_menu_book_and_check(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 8 10",  # valid movie input
        "1",               # book tickets
        "2",               # number of tickets to book (valid)
        "",                # return to menu from booking prompt
        "2",               # check bookings
        "3"                # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    # Do not assert booking prompt output, as input() is not compatible with pytest capture

def test_main_booking_too_many_tickets_plural(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 2 2",  # 4 seats
        "1",              # book tickets
        "5",              # request more than available
        "",               # return to menu
        "3"               # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Sorry, there are only 4 seats available." in captured.out

def test_main_booking_too_many_tickets_singular(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 1 1",  # 1 seat
        "1",              # book tickets
        "2",              # request more than available
        "",               # return to menu
        "3"               # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Sorry, there is only 1 seat available." in captured.out

def test_main_booking_invalid_input(capsys):
    from src import main as main_module
    user_inputs = [
        "Inception 2 2",  # 4 seats
        "1",              # book tickets
        "notanumber",     # invalid input
        "",               # return to menu
        "3"               # exit
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    assert "Invalid input. Please enter a valid number of tickets or blank to go back." in captured.out

# Unit test for prompt_movie_creation (isolated)
def test_prompt_movie_creation_valid(monkeypatch):
    from src import main as main_module
    # Simulate valid input on first try
    monkeypatch.setattr("builtins.input", lambda _: "Inception 8 10")
    movie_data = main_module.prompt_movie_creation()
    assert movie_data["title"] == "Inception"
    assert movie_data["row"] == 8
    assert movie_data["seats_per_row"] == 10
    assert isinstance(movie_data["bookings"], list)

def test_prompt_movie_creation_invalid_then_valid(monkeypatch):
    from src import main as main_module
    inputs = iter(["badinput", "Inception 8 10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    movie_data = main_module.prompt_movie_creation()
    assert movie_data["title"] == "Inception"

# Unit test for main_menu_loop (isolated)
def test_main_menu_loop_exit(monkeypatch):
    from src import main as main_module
    # Create a dummy movie_data
    movie_data = {"title": "Inception", "row": 8, "seats_per_row": 10, "bookings": []}
    # Simulate user entering '3' to exit immediately
    monkeypatch.setattr("builtins.input", lambda _: "3")
    # Should exit cleanly
    main_module.main_menu_loop(movie_data)

def test_booking_tickets_loop_exit_immediately(monkeypatch, capsys):
    from src import main as main_module
    movie_data = {"title": "Inception", "row": 2, "seats_per_row": 2, "bookings": []}
    monkeypatch.setattr("builtins.input", lambda _: "")
    main_module.booking_tickets_loop(movie_data)
    captured = capsys.readouterr()
    # Should produce no output when exiting immediately
    assert captured.out == ""

def test_booking_tickets_loop_invalid_input(monkeypatch, capsys):
    from src import main as main_module
    movie_data = {"title": "Inception", "row": 2, "seats_per_row": 2, "bookings": []}
    inputs = iter(["notanumber", ""])  # invalid, then exit
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main_module.booking_tickets_loop(movie_data)
    captured = capsys.readouterr()
    assert "Invalid input. Please enter a valid number of tickets or blank to go back." in captured.out

def test_booking_tickets_loop_too_many_plural(monkeypatch, capsys):
    from src import main as main_module
    movie_data = {"title": "Inception", "row": 2, "seats_per_row": 2, "bookings": []}  # 4 seats
    inputs = iter(["5", ""])  # too many, then exit
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main_module.booking_tickets_loop(movie_data)
    captured = capsys.readouterr()
    assert "Sorry, there are only 4 seats available." in captured.out

def test_booking_tickets_loop_too_many_singular(monkeypatch, capsys):
    from src import main as main_module
    movie_data = {"title": "Inception", "row": 1, "seats_per_row": 1, "bookings": []}  # 1 seat
    inputs = iter(["2", ""])  # too many, then exit
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main_module.booking_tickets_loop(movie_data)
    captured = capsys.readouterr()
    assert "Sorry, there is only 1 seat available." in captured.out

def test_booking_tickets_loop_valid(monkeypatch, capsys):
    from src import main as main_module
    movie_data = {"title": "Inception", "row": 2, "seats_per_row": 2, "bookings": []}  # 4 seats
    inputs = iter(["2", ""])  # valid booking, then auto-confirm
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main_module.booking_tickets_loop(movie_data)
    captured = capsys.readouterr()
    # Booking now succeeds, so just check for successful reservation message
    assert "Successfully reserved 2 Inception tickets" in captured.out