"""
test_end_to_end.py
-----------------
End-to-end test for the main booking and checking flows, based on a real user session.
"""

import pytest
from unittest import mock
from src import main as main_module

def test_end_to_end_booking_and_checking_flow(capsys):
    user_inputs = [
        # Movie creation
        "Avatar 2: The Way of Water 6 15",
        # Book 4 tickets (accept default)
        "1", "4", "",  # book, 4 tickets, accept
        # Book 7 tickets, try A5, then B5, accept
        "1", "7", "A5", "B5", "",  # book, 7 tickets, try custom seats
        # Book 16 tickets, try A5, invalid B9, F13, E8, accept
        "1", "16", "A5", "B9", "F13", "E8", "",  # book, 16 tickets, try custom seats
        # Book too many (70), then 2, try D2, accept
        "1", "70", "2", "D2", "",  # book, too many, then 2, custom seat
        # Check bookings: try invalid IDs, then valid ones, then blank to exit
        "2", "1", "GIC1", "booking1", "0001", "GIC001", "GIC0001", "GIC0002", "*", "\n", "",  # check bookings
        # Exit
        "3"
    ]
    with mock.patch("builtins.input", side_effect=user_inputs):
        main_module.main()
    captured = capsys.readouterr()
    out = captured.out

    # Minimal success path assertions
    assert "Welcome to the GIC CBS application!" in out
    assert "Welcome to GIC Cinemas" in out
    assert "Thank you for using GIC Cinemas system. Bye!" in out
    assert "Successfully reserved 4 Avatar 2: The Way of Water tickets." in out
    assert "Successfully reserved 7 Avatar 2: The Way of Water tickets." in out
    assert "Successfully reserved 16 Avatar 2: The Way of Water tickets." in out
    assert "Successfully reserved 2 Avatar 2: The Way of Water tickets." in out
    assert "Sorry, there are only 63 seats available." in out
    assert "Booking ID: GIC0001 confirmed." in out
    assert "Booking ID: GIC0002 confirmed." in out
    assert "Booking ID: GIC0003 confirmed." in out
    assert "Booking ID: GIC0004 confirmed." in out
    # Check for seat selection prompts and error handling
    assert "Seat B9 is not valid. Please try again or enter blank to accept." in out
    assert "Booking ID '1' not found. Please try again." in out
    assert "Booking ID 'GIC1' not found. Please try again." in out
    assert "Booking ID 'booking1' not found. Please try again." in out
    assert "Booking ID '0001' not found. Please try again." in out
    assert "Booking ID 'GIC001' not found. Please try again." in out
    assert "Booking ID '*' not found. Please try again." in out
    assert "Returning to main menu." in out
    # Check for correct seat map output (spot check)
    assert "Selected seats:" in out
    assert "S C R E E N" in out
    # Spot check for booking IDs in check flow
    assert "Booking ID: GIC0001" in out
    assert "Booking ID: GIC0002" in out
