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
import pytest
from src import validation

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
