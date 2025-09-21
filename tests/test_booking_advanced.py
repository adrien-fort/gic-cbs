"""
test_booking_advanced.py
-----------------------
Unit tests for the advanced booking module, covering contiguous block assignment and advanced seat logic.
"""

import pytest
import builtins
from unittest.mock import patch
from src.booking_advanced import block_center, find_contiguous_blocks, default_seating_advanced, find_contiguous_blocks
from src.booking_advanced import _find_best_block_in_row, _find_first_row_with_block, book_ticket_advanced
from src.movie import create_movie

## Tests for block_center
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
    # Empty block
    assert block_center([], 8) == float('inf')

## Tests for find_contiguous_blocks
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

## Tests for _find_best_block_in_row
def test__find_best_block_in_row_basic():
    # Simple case: one block big enough
    available = ["A1", "A2", "A3", "A4", "A5"]
    result = _find_best_block_in_row(available, 5, 3)
    assert result == ["A2", "A3", "A4"]

def test__find_best_block_in_row_tiebreak_rightmost():
    # Two blocks equally central, rightmost should be chosen
    available = ["A1", "A2", "A4", "A5"]
    # For 5 seats, center is 3; blocks: [A1, A2], [A4, A5]
    # Request 2 seats: both blocks equally distant, rightmost (A4, A5) should be chosen
    result = _find_best_block_in_row(available, 5, 2)
    assert result == ["A4", "A5"]

def test__find_best_block_in_row_no_block():
    # No block big enough
    available = ["A1", "A3", "A5"]
    result = _find_best_block_in_row(available, 5, 2)
    assert result is None

def test__find_best_block_in_row_multiple_blocks():
    # Multiple blocks, only one big enough
    available = ["A1", "A2", "A4", "A5", "A6"]
    # Blocks: [A1, A2], [A4, A5, A6]
    result = _find_best_block_in_row(available, 6, 3)
    assert result == ["A4", "A5", "A6"]

## Tests for _find_first_row_with_block
def test__find_first_row_with_block_basic():
    # 2 rows, 4 seats per row, only row B has a block of 3
    seat_map = {'A': ['A1', 'A2', 'A3', 'A4'], 'B': ['B1', 'B2', 'B3', 'B4']}
    booked = {'A1', 'A2', 'A3', 'A4'}
    assigned = []
    result = _find_first_row_with_block(2, seat_map, booked, assigned, 4, 3)
    assert result == ['B1', 'B2', 'B3']

def test__find_first_row_with_block_skips_rows():
    # 3 rows, only row C has a block of 2
    seat_map = {'A': ['A1', 'A2'], 'B': ['B1', 'B2'], 'C': ['C1', 'C2']}
    booked = {'A1', 'A2', 'B1', 'B2'}
    assigned = []
    result = _find_first_row_with_block(3, seat_map, booked, assigned, 2, 2)
    assert result == ['C1', 'C2']

def test__find_first_row_with_block_none():
    # No row has a block of 2
    seat_map = {'A': ['A1'], 'B': ['B1']}
    booked = set()
    assigned = []
    result = _find_first_row_with_block(2, seat_map, booked, assigned, 1, 2)
    assert result is None

## Tests for default_seating_advanced
def test_default_seating_advanced_all_contiguous():
    # 2 rows, 5 seats per row, all seats free, request 4
    movie = create_movie("TestMovie 2 5")
    assigned = default_seating_advanced(movie, 4)
    # Should assign most central block in row A: A2, A3, A4, A5
    assert set(assigned) == set(["A2", "A3", "A4", "A5"])

def test_default_seating_advanced_partial_blocks():
    # 1 row, 5 seats, A3 booked, request 3
    movie = create_movie("TestMovie 1 5")
    movie["bookings"] = [{"ID": "GIC0001", "status": "B", "seats": ["A3"]}]
    assigned = default_seating_advanced(movie, 3)
    # Should assign A2, A4, A5 (most central available)
    assert set(assigned) == set(["A2", "A4", "A5"])

def test_default_seating_advanced_skips_booked():
    # 2 rows, 4 seats per row, some seats booked, request 4
    movie = create_movie("TestMovie 2 4")
    movie["bookings"] = [{"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "B1"]}]
    assigned = default_seating_advanced(movie, 4)
    # Should assign A1, A4, B2, B3 (most central available)
    assert set(assigned) == set(["A1", "A4", "B2", "B3"])

def test_default_seating_advanced_not_enough_seats():
    # 1 row, 3 seats, all booked, request 2
    movie = create_movie("TestMovie 1 3")
    movie["bookings"] = [{"ID": "GIC0001", "status": "B", "seats": ["A1", "A2", "A3"]}]
    assigned = default_seating_advanced(movie, 2)
    # Should return empty list
    assert assigned == []

def test_default_seating_advanced_exact_fit():
    # 1 row, 3 seats, request all
    movie = create_movie("TestMovie 1 3")
    assigned = default_seating_advanced(movie, 3)
    assert set(assigned) == set(["A1", "A2", "A3"])

## Tests for book_ticket_advanced (end to end)
def test_default_seating_advanced_large_group_with_blocked_row():
    movie = create_movie("Inception 8 10")
    # Book B3, B4, B5, B6
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["B3", "B4", "B5", "B6"]}
    ]
    # New booking for 12 seats should fill all of row A and then B7, B8
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 12)
    expected_seats = set([f"A{i}" for i in range(1, 11)] + ["B7", "B8"])
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == expected_seats

def test_default_seating_advanced_with_sparse_bookings():
    movie = create_movie("Inception 8 10")
    # Book specific seats in A
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A4", "A5", "A7", "A9"]}
    ]
    # New booking for 3 seats should get B5, B6, B4 (most central in next available row)
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 3)
    assigned_seats = movie["bookings"][-1]["seats"]
    assert set(assigned_seats) == set(["B5", "B6", "B4"])

def test_book_ticket_advanced_adds_booking():
    movie = create_movie("Inception 8 10")
    # Book 2 tickets, expect a booking object to be added
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        updated_movie = book_ticket_advanced(movie, 2)
    assert len(updated_movie["bookings"]) == 1
    booking = updated_movie["bookings"][0]
    assert booking["ID"] == "GIC0001"
    assert booking["status"] == "B"
    assert len(booking["seats"]) == 2

def test_default_seating_advanced_first_booking_single():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 1)
    assigned_seats = movie["bookings"][0]["seats"]
    assert assigned_seats == ["A5"]

def test_default_seating_advanced_first_booking_group():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 3)
    assigned_seats = movie["bookings"][0]["seats"]
    # Should assign A5, A4, A6 (center, then left, then right)
    assert set(assigned_seats) == set(["A5", "A4", "A6"])

def test_default_seating_advanced_with_existing_bookings():
    movie = create_movie("Inception 8 10")
    # First booking takes A5
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 1)
        # Second booking for 2 seats
        movie = book_ticket_advanced(movie, 2)
        assigned_seats = movie["bookings"][1]["seats"]
        # Should assign A6, A7 (rightmost contiguous seats after A5 is booked)
        assert assigned_seats == ["A6", "A7"]

def test_default_seating_advanced_with_existing_random_groups():
    movie = create_movie("Inception 2 6")  # Rows: A, B; Seats: 1-6
    # Existing bookings: A2, A3, A4 (middle block taken)
    movie["bookings"] = [
        {"ID": "GIC0001", "status": "B", "seats": ["A2", "A3", "A4"]}
    ]
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        # New booking for 2 seats should get A5, A6
        movie = book_ticket_advanced(movie, 2)
        assert movie["bookings"][-1]["seats"] == ["A5", "A6"]
        # New booking for 2 seats should get B3, B4 as it is the next best contiguous block of seats for two people
        movie = book_ticket_advanced(movie, 2)
        assigned_seats2 = movie["bookings"][-1]["seats"]
        assert assigned_seats2 == ["B3", "B4"]  # B3, B4 are the most middle in B

