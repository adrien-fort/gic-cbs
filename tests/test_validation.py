"""
test_validation.py
-----------------
Unit tests for the validation module, covering input validation for movies, tickets, and seats.
"""

import pytest
from src import validation

def test_movie_validation():
    from src.validation import movie_validation
    # True cases
    assert movie_validation("Inception 8 10") is True
    assert movie_validation("Die Hard 2 16 45") is True

    # False cases
    # Not enough parts
    assert movie_validation("") is False
    assert movie_validation("Inception 8") is False
    # Non-string input
    assert movie_validation(None) is False
    assert movie_validation(123) is False
    # Title is empty
    assert movie_validation(" 8 10") is False
    # Row is not a number
    assert movie_validation("Inception X 10") is False
    # SeatsPerRow is not a number
    assert movie_validation("Inception 8 X") is False
    # Row is zero
    assert movie_validation("Inception 0 10") is False
    # SeatsPerRow is zero
    assert movie_validation("Inception 8 0") is False
    # Row is negative
    assert movie_validation("Inception -1 10") is False
    # SeatsPerRow is negative
    assert movie_validation("Inception 8 -5") is False
    # Row exceeds 26
    assert movie_validation("Inception 27 10") is False
    # SeatsPerRow exceeds 50
    assert movie_validation("Inception 8 51") is False

def test_is_positive_integer():
    assert validation.is_positive_integer(5) is True
    assert validation.is_positive_integer("10") is True
    assert validation.is_positive_integer(0) is False
    assert validation.is_positive_integer(-3) is False
    assert validation.is_positive_integer("abc") is False
    assert validation.is_positive_integer(None) is False

def test_ticket_num_validation():
    from src.validation import ticket_num_validation
    from src.movie import create_movie
    # Empty cinema: Inception 8 10 (80 seats)
    movie = create_movie("Inception 8 10")
    assert ticket_num_validation("4", movie) is True
    assert ticket_num_validation("81", movie) is False
    # 6 seats already booked
    movie_with_booked = create_movie("Inception 8 10")
    movie_with_booked["bookings"].append({
        "ID": "GIC0001",
        "status": "B",
        "seats": ["A1", "A2", "A3", "A4", "A5", "A6"]
    })
    assert ticket_num_validation("78", movie_with_booked) is False

def test_is_valid_seat_positive():
    from src.validation import is_valid_seat
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    # No bookings, seat is unoccupied
    assert is_valid_seat(movie, "A2") == "valid"

def test_is_valid_seat_reserved():
    from src.validation import is_valid_seat
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    movie["bookings"].append({"ID": "GIC0001", "status": "R", "seats": ["A2"]})
    assert is_valid_seat(movie, "A2") == "valid"

def test_is_valid_seat_booked():
    from src.validation import is_valid_seat
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    movie["bookings"].append({"ID": "GIC0001", "status": "B", "seats": ["A2"]})
    assert is_valid_seat(movie, "A2") == "invalid"

def test_is_valid_seat_nonexistent():
    from src.validation import is_valid_seat
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    assert is_valid_seat(movie, "Z99") == "invalid"

def test_is_valid_booking_false_for_nonexistent():
    from src.validation import is_valid_booking
    movie_json = {
        "title": "Inception",
        "row": 8,
        "seats_per_row": 8,
        "bookings": [
            {"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
            {"ID": "GIC0002", "status": "B", "seats": ["A3", "A4"]},
        ]
    }
    assert is_valid_booking(movie_json, "GIC0003") is False

def test_is_valid_booking_true_for_existing():
    from src.validation import is_valid_booking
    movie_json = {
        "title": "Inception",
        "row": 8,
        "seats_per_row": 8,
        "bookings": [
            {"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
            {"ID": "GIC0002", "status": "B", "seats": ["A3", "A4"]},
        ]
    }
    assert is_valid_booking(movie_json, "GIC0002") is True

def test_is_valid_booking_false_for_random_inputs():
    from src.validation import is_valid_booking
    movie_json = {
        "title": "Inception",
        "row": 8,
        "seats_per_row": 8,
        "bookings": [
            {"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
            {"ID": "GIC0002", "status": "B", "seats": ["A3", "A4"]},
        ]
    }
    for invalid in [None, "", "booking01", "GIC", "0001", 123, [], {}, "GIC9999"]:
        assert is_valid_booking(movie_json, invalid) is False