import pytest
import builtins
from unittest.mock import patch
from src.movie import create_movie
from src.booking import get_row_center, seat_sort_order, book_ticket, default_seating
from src.booking import seat_sort_order, build_seat_map, get_booked_seats, get_booking_id
from src.booking import confirm_reservation, ordered_free_seat_map
 

# Tests for ordered_free_seat_map
def test_ordered_free_seat_map_2x3():
    # Inception 2 3, no bookings
    seat_map = build_seat_map({"row": 2, "seats_per_row": 3})
    booked = set()
    result = ordered_free_seat_map(seat_map, booked)
    assert result == ["A2", "A3", "A1", "B2", "B3", "B1"]

def test_ordered_free_seat_map_2x4():
    # Inception 2 4, no bookings
    seat_map = build_seat_map({"row": 2, "seats_per_row": 4})
    booked = set()
    result = ordered_free_seat_map(seat_map, booked)
    assert result == ["A3", "A2", "A4", "A1", "B3", "B2", "B4", "B1"]

def test_ordered_free_seat_map_2x3_with_booked():
    seat_map = build_seat_map({"row": 2, "seats_per_row": 3})
    booked = {"A2", "B3"}
    result = ordered_free_seat_map(seat_map, booked)
    assert result == ["A3", "A1", "B2", "B1"]  # A2 and B3 removed

def test_ordered_free_seat_map_2x4_with_booked():
    seat_map = build_seat_map({"row": 2, "seats_per_row": 4})
    booked = {"A3", "A2", "B2"}
    result = ordered_free_seat_map(seat_map, booked)
    assert result == ["A4", "A1", "B3", "B4", "B1"]  # A3, A2, B2 removed

## Tests for get_row_center
def test_get_row_center_even():
    assert get_row_center(10) == 5
    assert get_row_center(8) == 4

def test_get_row_center_odd():
    assert get_row_center(9) == 5
    assert get_row_center(7) == 4

## Tests for seat_sort_order
def test_seat_sort_order_various():

    seats = ["A1", "A2", "A3", "A4", "A5"]
    assert seat_sort_order(seats, 5) == ["A3", "A4", "A2", "A5", "A1"]

    # Even seats, center is 4
    seats = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    # Most central: B4, B5, then rightmost if tied
    assert seat_sort_order(seats, 8)[:4] == ["B5", "B4", "B6", "B3"]

def test_seat_sort_order_even_row_rightmost_central():
    seats = [f"A{i}" for i in range(1, 11)]
    # For 10 seats, central seats are A5 and A6, rightmost (A6) should come first
    from src.booking import seat_sort_order
    assert seat_sort_order(seats, 10, take=1) == ["A6"]

def test_seat_sort_order_tiebreak_rightmost():
    seats = ["C1", "C2", "C3", "C4"]
    # Center is 2, so C2 and C3 are equally central, C3 (rightmost) comes first
    assert seat_sort_order(seats, 4)[:2] == ["C3", "C2"]

def test_seat_sort_order_take():
    seats = ["B1", "B2", "B3", "B4", "B5", "B6"]
    # For 6 seats, center is 3 so B3 and B4 are equally central, B4 (rightmost) comes first
    assert seat_sort_order(seats, 6, take=3) == ["B4", "B3", "B5"]

def test_seat_sort_order_empty():
    assert seat_sort_order([], 5) == []

## Test for build_seat_map
def test_build_seat_map_basic():
    movie_json = {"row": 2, "seats_per_row": 3}
    seat_map = build_seat_map(movie_json)
    assert seat_map == {
        'A': ['A1', 'A2', 'A3'],
        'B': ['B1', 'B2', 'B3']
    }

## Tests for get_booked_seats
def test_get_booked_seats_empty():
    movie_json = {"bookings": []}
    assert get_booked_seats(movie_json) == set()

def test_get_booked_seats_with_bookings():
    movie_json = {
        "bookings": [
            {"ID": "GIC0001", "status": "B", "seats": ["A1", "A2"]},
            {"ID": "GIC0002", "status": "B", "seats": ["B3"]}
        ]
    }
    assert get_booked_seats(movie_json) == {"A1", "A2", "B3"}

## Tests for get_booking_id
def test_get_booking_id_empty():
    movie = create_movie("Inception 8 10")
    assert get_booking_id(movie) == "GIC0001"

def test_get_booking_id_with_existing():
    movie = create_movie("Inception 8 10")
    # Add two bookings with IDs GIC0001 and GIC0002
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A1"]},
        {"ID": "GIC0002", "status": "B", "seats": ["A2"]}
    ]
    assert get_booking_id(movie) == "GIC0003"

def test_get_booking_id_with_gap():
    movie = create_movie("Inception 8 10")
    # Add bookings with IDs GIC0001 and GIC0003 (gap)
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A1"]},
        {"ID": "GIC0003", "status": "B", "seats": ["A3"]}
    ]
    # Should return GIC0004 (next after max)
    assert get_booking_id(movie) == "GIC0004"

## Tests for confirm_reservation
def test_confirm_reservation_changes_status():
    # Create a movie and add a booking with status 'R'
    movie = create_movie("Inception 8 10")
    booking_id = "GIC0001"
    movie["bookings"] = [
        {"ID": booking_id, "status": "R", "seats": ["A1", "A2"]}
    ]
    updated_movie = confirm_reservation(movie, booking_id)
    assert updated_movie["bookings"][0]["status"] == "B"

def test_confirm_reservation_does_not_change_other_bookings():
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

# --- Tests for default_seating
def test_default_seating_basic_2_seats():
    movie = create_movie("Inception 3 3")
    assigned = default_seating(movie, 2)
    assert assigned == ["A2", "A3"]

def test_default_seating_basic_4_seats():
    movie = create_movie("Inception 3 3")
    assigned = default_seating(movie, 4)
    assert assigned == ["A2", "A3", "A1", "B2"]

def test_default_seating_with_bookings_small_group():
    movie = create_movie("Inception 4 5")
    # Book some seats
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "B2"]},
        {"ID": "GIC0002", "status": "B", "seats": ["C3"]}
    ]
    assigned = default_seating(movie, 3)
    # Should pick most central available: A4, A5, A1
    assert assigned == ["A4", "A5", "A1"]

def test_default_seating_with_bookings_large_group():
    movie = create_movie("Inception 5 6")
    # Book some seats
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "A4", "B3", "C2", "D5", "E1"]}
    ]
    assigned = default_seating(movie, 7)
    # Should pick most central available: A5, A6, A1, B4, B5, B2, B6
    assert assigned == ["A5", "A6", "A1", "B4", "B5", "B2", "B6"]

## Tests for book_ticket (end to end)
def test_default_seating_large_group_with_blocked_row():
    movie = create_movie("Inception 8 10")
    # Book B3, B4, B5, B6
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["B3", "B4", "B5", "B6"]}
    ]
    # New booking for 12 seats should fill all of row A and then B7, B8
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 12)
    expected_seats = set([f"A{i}" for i in range(1, 11)] + ["B7", "B8"])
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == expected_seats

def test_default_seating_with_sparse_bookings():
    movie = create_movie("Inception 8 10")
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A4", "A5", "A7", "A9"]}
    ]
    # New booking for 3 seats should get A6, A8, A3
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 3)
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == set(["A6", "A8", "A3"])

def test_book_ticket_adds_booking():
    movie = create_movie("Inception 8 10")
    # Book 2 tickets, expect a booking object to be added
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        updated_movie = book_ticket(movie, 2)
    assert len(updated_movie["bookings"]) == 1
    booking = updated_movie["bookings"][0]
    assert booking["ID"] == "GIC0001"
    assert booking["status"] == "B"
    assert len(booking["seats"]) == 2

def test_default_seating_first_booking_single():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 1)
    assigned_seats = movie["bookings"][0]["seats"]
    assert assigned_seats == ["A6"]

def test_default_seating_first_booking_group():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 3)
    assigned_seats = movie["bookings"][0]["seats"]
    # Should assign A6, A5, A7 (center rightmost, center leftmost, then rightmost)
    assert set(assigned_seats) == set(["A6", "A5", "A7"])

def test_default_seating_with_existing_bookings():
    movie = create_movie("Inception 8 10")
    # First booking takes A5
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 1)
        # Second booking for 2 seats
        movie = book_ticket(movie, 2)
        assigned_seats = movie["bookings"][1]["seats"]
        # Should assign A5, A7
        assert assigned_seats == ["A5", "A7"]

def test_default_seating_with_existing_random_groups():
    movie = create_movie("Inception 2 6")  # Rows: A, B; Seats: 1-6
    # Existing bookings: A2, A3, A4 (middle block taken)
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "A4"]}
    ]
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        # New booking for 2 seats should get A5, A6
        movie = book_ticket(movie, 2)
        assert movie["bookings"][-1]["seats"] == ["A5", "A6"]
        # New booking for 2 seats should get A1 and B4
        movie = book_ticket(movie, 2)
        assigned_seats2 = movie["bookings"][-1]["seats"]
        assert assigned_seats2 == ["A1", "B4"]  # A1, B4 are the most middle in A, B

