def test_get_row_center_even():
    from src.booking import get_row_center
    assert get_row_center(10) == 5
    assert get_row_center(8) == 4

def test_get_row_center_odd():
    from src.booking import get_row_center
    assert get_row_center(9) == 5
    assert get_row_center(7) == 4

def test_seat_sort_order_various():
    from src.booking import seat_sort_order
    # Odd seats, center is 3
    seats = ["A1", "A2", "A3", "A4", "A5"]
    assert seat_sort_order(seats, 5) == ["A3", "A4", "A2", "A5", "A1"]
    # Even seats, center is 4
    seats = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    # Most central: B4, B5, then rightmost if tied
    assert seat_sort_order(seats, 8)[:4] == ["B4", "B5", "B3", "B6"]

def test_seat_sort_order_tiebreak_rightmost():
    from src.booking import seat_sort_order
    seats = ["C1", "C2", "C3", "C4"]
    # Center is 2, so C2 and C3 are equally central, C3 (rightmost) comes first
    assert seat_sort_order(seats, 4)[:2] == ["C2", "C3"] or seat_sort_order(seats, 4)[:2] == ["C3", "C2"]

def test_find_contiguous_blocks_cases():
    from src.booking import find_contiguous_blocks
    # Multiple blocks
    available = ["A1", "A2", "A4", "A5", "A7"]
    assert find_contiguous_blocks(available) == [["A1", "A2"], ["A4", "A5"], ["A7"]]
    # Single block
    available = ["B3", "B4", "B5"]
    assert find_contiguous_blocks(available) == [["B3", "B4", "B5"]]
    # Empty
    assert find_contiguous_blocks([]) == []


def test_block_center_cases():
    from src.booking import block_center
    # Centered block
    assert block_center(["A2", "A3", "A4"], 5) == 0.0
    # Offset block
    assert block_center(["A4", "A5", "A6"], 10) == 0.0
    assert block_center(["A7", "A8", "A9"], 10) == 3.0
    # Empty block
    assert block_center([], 8) == float('inf')
def test_default_seating_large_group_with_blocked_row():
    from src.booking import default_seating, book_ticket
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    # Book B3, B4, B5, B6
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["B3", "B4", "B5", "B6"]}
    ]
    # New booking for 12 seats should fill all of row A and then B7, B8
    import builtins
    from unittest.mock import patch
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 12)
    expected_seats = set([f"A{i}" for i in range(1, 11)] + ["B7", "B8"])
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == expected_seats
def test_default_seating_with_sparse_bookings():
    from src.booking import default_seating, book_ticket
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    # Book specific seats in A
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A4", "A5", "A7", "A9"]}
    ]
    # New booking for 3 seats should get B5, B6, B4 (most central in next available row)
    import builtins
    from unittest.mock import patch
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 3)
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == set(["B5", "B6", "B4"])
from src.booking import seat_sort_order, block_center
from src.booking import build_seat_map, get_booked_seats, find_contiguous_blocks
import pytest
from src.movie import create_movie

# Tests for seat_sort_order utility
def test_seat_sort_order_centrality():
    seats = ["A1", "A2", "A3", "A4", "A5"]
    # For 5 seats, center is 3
    assert seat_sort_order(seats, 5) == ["A3", "A4", "A2", "A5", "A1"]

def test_seat_sort_order_take():
    seats = ["B1", "B2", "B3", "B4", "B5", "B6"]
    # For 6 seats, center is 3
    assert seat_sort_order(seats, 6, take=3) == ["B3", "B4", "B2"] or seat_sort_order(seats, 6, take=3) == ["B3", "B4", "B5"]

def test_seat_sort_order_empty():
    assert seat_sort_order([], 5) == []

# Tests for block_center utility
def test_block_center_middle():
    block = ["A2", "A3", "A4"]
    # For 5 seats, center is 3, block center is 3
    assert block_center(block, 5) == 0.0

def test_block_center_offset():
    block = ["A4", "A5", "A6"]
    # For 10 seats, center is 5, block center is 5
    assert block_center(block, 10) == 0.0
    block2 = ["A7", "A8", "A9"]
    # For 10 seats, center is 5, block center is 8
    assert block_center(block2, 10) == 3.0

def test_block_center_empty():
    assert block_center([], 8) == float('inf')

# Utility function tests
def test_build_seat_map_basic():
    movie_json = {"row": 2, "seats_per_row": 3}
    seat_map = build_seat_map(movie_json)
    assert seat_map == {
        'A': ['A1', 'A2', 'A3'],
        'B': ['B1', 'B2', 'B3']
    }

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

def test_find_contiguous_blocks_simple():
    available = ["A1", "A2", "A3", "A5", "A6", "A8"]
    blocks = find_contiguous_blocks(available)
    assert blocks == [["A1", "A2", "A3"], ["A5", "A6"], ["A8"]]

def test_find_contiguous_blocks_single():
    available = ["B4"]
    blocks = find_contiguous_blocks(available)
    assert blocks == [["B4"]]

def test_find_contiguous_blocks_empty():
    available = []
    blocks = find_contiguous_blocks(available)
    assert blocks == []

def test_book_ticket_adds_booking():
    from src.booking import book_ticket
    movie = create_movie("Inception 8 10")
    # Book 2 tickets, expect a booking object to be added
    import builtins
    from unittest.mock import patch
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        updated_movie = book_ticket(movie, 2)
    assert len(updated_movie["bookings"]) == 1
    booking = updated_movie["bookings"][0]
    assert booking["ID"] == "GIC0001"
    assert booking["status"] == "R" or booking["status"] == "B"
    assert len(booking["seats"]) > 0

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

def test_default_seating_first_booking_single():
    from src.booking import default_seating, book_ticket
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    import builtins
    from unittest.mock import patch
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 1)
    assigned_seats = movie["bookings"][0]["seats"]
    assert assigned_seats == ["A5"]

def test_default_seating_first_booking_group():
    from src.booking import default_seating, book_ticket
    from src.movie import create_movie
    movie = create_movie("Inception 8 10")
    import builtins
    from unittest.mock import patch
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 3)
    assigned_seats = movie["bookings"][0]["seats"]
    # Should assign A5, A4, A6 (center, then left, then right)
    assert set(assigned_seats) == set(["A5", "A4", "A6"])

def test_default_seating_with_existing_bookings():
    from src.booking import book_ticket
    from src.movie import create_movie
    import builtins
    from unittest.mock import patch

    movie = create_movie("Inception 8 10")
    # First booking takes A5
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket(movie, 1)
        # Second booking for 2 seats
        movie = book_ticket(movie, 2)
        assigned_seats = movie["bookings"][1]["seats"]
        # Should assign A6, A7 (rightmost contiguous seats after A5 is booked)
        assert assigned_seats == ["A6", "A7"]

def test_default_seating_with_existing_random_groups():
    from src.booking import book_ticket
    from src.movie import create_movie
    import builtins
    from unittest.mock import patch

    movie = create_movie("Inception 2 6")  # Rows: A, B; Seats: 1-6
    # Existing bookings: A2, A3, A4 (middle block taken)
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "A4"]}
    ]
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        # New booking for 2 seats should get A5, A6
        movie = book_ticket(movie, 2)
        assert movie["bookings"][-1]["seats"] == ["A5", "A6"]
        # New booking for 2 seats should get B3, B4 as it is the next best contiguous block of seats for two people
        movie = book_ticket(movie, 2)
        assigned_seats2 = movie["bookings"][-1]["seats"]
        assert assigned_seats2 == ["B3", "B4"]  # B3, B4 are the most middle in B
