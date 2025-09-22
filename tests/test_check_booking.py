"""
test_check_booking.py
--------------------
Unit tests for the check_booking module (booking listing and display).
"""

import pytest
from copy import deepcopy
from src.check_booking import unbook_reservation, view_booking

def test_unbook_reservation_sets_status_reserved():
    from src.movie_classes import Movie, Booking
    movie = Movie(
        "Inception",
        8,
        8,
        bookings=[
            Booking("GIC0001", "B", ["A1", "A2"]),
            Booking("GIC0002", "B", ["A3", "A4"]),
            Booking("GIC0003", "B", ["A5", "A6"]),
        ]
    )
    result = unbook_reservation(movie, "GIC0002")
    statuses = {b.id: b.status for b in result.bookings}
    assert statuses["GIC0001"] == "B"
    assert statuses["GIC0002"] == "R"
    assert statuses["GIC0003"] == "B"

def test_view_booking_does_not_modify_movie_json():
    from src.movie_classes import Movie, Booking
    # Setup: movie with two bookings
    movie = Movie(
        "Avatar 2",
        3,
        7,
        bookings=[
            Booking("GIC0001", "B", ["A1", "A2"]),
            Booking("GIC0002", "B", ["B3", "B4"]),
        ]
    )
    original = deepcopy(movie)
    # Call view_booking for both valid and invalid IDs
    result1 = view_booking(movie, "GIC0001")
    result2 = view_booking(movie, "GIC0002")
    result3 = view_booking(movie, "GIC9999")
    # Assert movie is unchanged after all calls
    assert movie.to_dict() == original.to_dict()
    assert result1.to_dict() == original.to_dict()
    assert result2.to_dict() == original.to_dict()
    assert result3.to_dict() == original.to_dict()