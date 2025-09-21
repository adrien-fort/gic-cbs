"""
test_check_booking.py
--------------------
Unit tests for the check_booking module (booking listing and display).
"""

import pytest
from copy import deepcopy
from src.check_booking import unbook_reservation, view_booking

def test_unbook_reservation_sets_status_reserved():
	movie_json = {
		"title": "Inception",
		"row": 8,
		"seats_per_row": 8,
		"bookings": [
			{"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
			{"ID": "GIC0002", "status": "B", "seats": ["A3", "A4"]},
			{"ID": "GIC0003", "status": "B", "seats": ["A5", "A6"]},
		]
	}
	result = unbook_reservation(movie_json, "GIC0002")
	statuses = {b["ID"]: b["status"] for b in result["bookings"]}
	assert statuses["GIC0001"] == "B"
	assert statuses["GIC0002"] == "R"
	assert statuses["GIC0003"] == "B"

def test_view_booking_does_not_modify_movie_json():
    # Setup: movie with two bookings
    movie_json = {
        "title": "Avatar 2",
        "row": 3,
        "seats_per_row": 7,
        "bookings": [
            {"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
            {"ID": "GIC0002", "status": "B", "seats": ["B3", "B4"]},
        ]
    }
    original = deepcopy(movie_json)
    # Call view_booking for both valid and invalid IDs
    result1 = view_booking(movie_json, "GIC0001")
    result2 = view_booking(movie_json, "GIC0002")
    result3 = view_booking(movie_json, "GIC9999")
    # Assert movie_json is unchanged after all calls
    assert movie_json == original
    assert result1 == original
    assert result2 == original
    assert result3 == original