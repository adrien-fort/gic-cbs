import pytest
from src.movie import create_movie

def test_book_ticket_adds_booking():
    from src.booking import book_ticket
    movie = create_movie("Inception 8 10")
    # Book 2 tickets, expect a booking object to be added
    updated_movie = book_ticket(movie, 2)
    assert len(updated_movie["bookings"]) == 1
    booking = updated_movie["bookings"][0]
    assert booking["ID"] == "GIC0001"
    assert booking["status"] == "B"
    assert booking["seats"] == ["A4", "A5"]

def test_get_booking_id_empty():
    from src.booking import get_booking_id
    movie = create_movie("Inception 8 10")
    assert get_booking_id(movie) == "GIC0001"

def test_get_booking_id_with_existing():
    from src.booking import get_booking_id
    movie = create_movie("Inception 8 10")
    # Add two bookings with IDs GIC0001 and GIC0002
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A1"]},
        {"ID": "GIC0002", "status": "B", "seats": ["A2"]}
    ]
    assert get_booking_id(movie) == "GIC0003"

def test_get_booking_id_with_gap():
    from src.booking import get_booking_id
    movie = create_movie("Inception 8 10")
    # Add bookings with IDs GIC0001 and GIC0003 (gap)
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A1"]},
        {"ID": "GIC0003", "status": "B", "seats": ["A3"]}
    ]
    # Should return GIC0004 (next after max)
    assert get_booking_id(movie) == "GIC0004"

def test_confirm_reservation_changes_status():
    from src.booking import confirm_reservation
    from src.movie import create_movie
    # Create a movie and add a booking with status 'R'
    movie = create_movie("Inception 8 10")
    booking_id = "GIC0001"
    movie["bookings"] = [
        {"ID": booking_id, "status": "R", "seats": ["A1", "A2"]}
    ]
    updated_movie = confirm_reservation(movie, booking_id)
    assert updated_movie["bookings"][0]["status"] == "B"

def test_confirm_reservation_does_not_change_other_bookings():
    from src.booking import confirm_reservation
    from src.movie import create_movie
    # Create a movie and add two bookings
    movie = create_movie("Inception 8 10")
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "R", "seats": ["A1"]},
        {"ID": "GIC0002", "status": "R", "seats": ["A2"]}
    ]
    updated_movie = confirm_reservation(movie, "GIC0002")
    assert updated_movie["bookings"][0]["status"] == "R"
    assert updated_movie["bookings"][1]["status"] == "B"

def test_confirm_reservation_nonexistent_id():
    from src.booking import confirm_reservation
    from src.movie import create_movie
    # Create a movie with one booking
    movie = create_movie("Inception 8 10")
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "R", "seats": ["A1"]}
    ]
    updated_movie = confirm_reservation(movie, "GIC9999")
    # No change expected
    assert updated_movie["bookings"][0]["status"] == "R"
