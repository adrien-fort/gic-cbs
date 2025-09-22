"""
test_booking_advanced.py
-----------------------
Unit tests for the advanced booking module, covering contiguous block assignment and advanced seat logic.
"""

import pytest
import builtins
from unittest.mock import patch
from src.movie_classes import Booking
from src.booking_advanced import block_center, default_seating_advanced, find_contiguous_blocks, advanced_custom_seating
from src.booking_advanced import _find_best_block_in_row, _find_first_row_with_block, book_ticket_advanced
from src.booking_advanced import assign_from_starting_seat, find_best_subblock, assign_overflow_rows, assign_fallback_seats
from src.movie import create_movie

## Tests for block_center
def test_block_center_middle():
    block = ["A2", "A3", "A4"]
    # For 5 seats, center is 3, block center is 3
    assert block_center(block, 5) == pytest.approx(0.0)

def test_block_center_offset():
    block = ["A4", "A5", "A6"]
    # For 10 seats, center is 5, block center is 5
    assert block_center(block, 10) == pytest.approx(0.0)
    block2 = ["A7", "A8", "A9"]
    # For 10 seats, center is 5, block center is 8
    assert block_center(block2, 10) == pytest.approx(3.0)

def test_block_center_empty():
    # Empty block should return inf
    assert block_center([], 5) == float('inf')

# Reinstate advanced booking flow tests as top-level functions
def test_book_ticket_advanced_exit_immediately(monkeypatch, capsys):
    from src.booking_advanced import book_ticket_advanced
    from src.movie_classes import Movie
    movie_obj = Movie("Inception", 2, 2)
    monkeypatch.setattr("builtins.input", lambda _: "")
    result = book_ticket_advanced(movie_obj, 2)
    assert result is movie_obj

def test_book_ticket_advanced_invalid_input(monkeypatch, capsys):
    from src.booking_advanced import book_ticket_advanced
    from src.movie_classes import Movie
    movie_obj = Movie("Inception", 2, 2)
    inputs = iter(["notanumber", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = book_ticket_advanced(movie_obj, 2)
    assert result is movie_obj

def test_book_ticket_advanced_too_many_plural(monkeypatch, capsys):
    from src.booking_advanced import book_ticket_advanced
    from src.movie_classes import Movie
    movie_obj = Movie("Inception", 2, 2)
    inputs = iter(["5", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = book_ticket_advanced(movie_obj, 2)
    assert result is movie_obj

def test_book_ticket_advanced_too_many_singular(monkeypatch, capsys):
    from src.booking_advanced import book_ticket_advanced
    from src.movie_classes import Movie
    movie_obj = Movie("Inception", 1, 1)
    inputs = iter(["2", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = book_ticket_advanced(movie_obj, 1)
    assert result is movie_obj

def test_book_ticket_advanced_valid(monkeypatch, capsys):
    from src.booking_advanced import book_ticket_advanced
    from src.movie_classes import Movie
    movie_obj = Movie("Inception", 2, 2)
    inputs = iter(["A1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = book_ticket_advanced(movie_obj, 2)
    assert result is movie_obj

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
    assert set(assigned) == {"A2", "A3", "A4", "A5"}

def test_default_seating_advanced_partial_blocks():
    # 1 row, 5 seats, A3 booked, request 3
    from src.movie_classes import Booking
    movie = create_movie("TestMovie 1 5")
    movie.bookings = [Booking("GIC0001", "B", ["A3"])]
    assigned = default_seating_advanced(movie, 3)
    # Should assign A2, A4, A5 (most central available)
    assert set(assigned) == {"A2", "A4", "A5"}

def test_default_seating_advanced_skips_booked():
    # 2 rows, 4 seats per row, some seats booked, request 4
    from src.movie_classes import Booking
    movie = create_movie("TestMovie 2 4")
    movie.bookings = [Booking("GIC0001", "B", ["A2", "A3", "B1"])]
    assigned = default_seating_advanced(movie, 4)
    # Should assign A1, A4, B2, B3 (most central available)
    assert set(assigned) == {"A1", "A4", "B2", "B3"}

def test_default_seating_advanced_not_enough_seats():
    # 1 row, 3 seats, all booked, request 2
    from src.movie_classes import Booking
    movie = create_movie("TestMovie 1 3")
    movie.bookings = [Booking("GIC0001", "B", ["A1", "A2", "A3"])]
    assigned = default_seating_advanced(movie, 2)
    # Should return empty list
    assert assigned == []

def test_default_seating_advanced_exact_fit():
    # 1 row, 3 seats, request all
    movie = create_movie("TestMovie 1 3")
    assigned = default_seating_advanced(movie, 3)
    assert set(assigned) == {"A1", "A2", "A3"}

## Tests for book_ticket_advanced (end to end)
def test_default_seating_advanced_large_group_with_blocked_row():
    from src.movie_classes import Booking
    movie = create_movie("Inception 8 10")
    # Book B3, B4, B5, B6
    movie.bookings = [Booking("GIC0001", "B", ["B3", "B4", "B5", "B6"])]
    # New booking for 12 seats should fill all of row A and then B7, B8
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 12)
    expected_seats = {f"A{i}" for i in range(1, 11)} | {"B7", "B8"}
    assigned_seats = movie.bookings[-1].seats
    assert set(assigned_seats) == expected_seats

def test_default_seating_advanced_with_sparse_bookings():
    from src.movie_classes import Booking
    movie = create_movie("Inception 8 10")
    # Book specific seats in A
    movie.bookings = [Booking("GIC0001", "B", ["A2", "A4", "A5", "A7", "A9"])]
    # New booking for 3 seats should get B5, B6, B4 (most central in next available row)
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 3)
    assigned_seats = movie.bookings[-1].seats
    assert set(assigned_seats) == {"B5", "B6", "B4"}

def test_book_ticket_advanced_adds_booking():
    movie = create_movie("Inception 8 10")
    # Book 2 tickets, expect a booking object to be added
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        updated_movie = book_ticket_advanced(movie, 2)
    assert len(updated_movie.bookings) == 1
    booking = updated_movie.bookings[0]
    assert booking.id == "GIC0001"
    assert booking.status == "B"
    assert len(booking.seats) == 2

def test_default_seating_advanced_first_booking_single():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 1)
    assigned_seats = movie.bookings[0].seats
    assert assigned_seats == ["A5"]

def test_default_seating_advanced_first_booking_group():
    movie = create_movie("Inception 8 10")
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 3)
    assigned_seats = movie.bookings[0].seats
    # Should assign A5, A4, A6 (center, then left, then right)
    assert set(assigned_seats) == {"A5", "A4", "A6"}

def test_default_seating_advanced_with_existing_bookings():
    movie = create_movie("Inception 8 10")
    # First booking takes A5
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        movie = book_ticket_advanced(movie, 1)
        # Second booking for 2 seats
        movie = book_ticket_advanced(movie, 2)
        assigned_seats = movie.bookings[1].seats
        # Should assign A6, A7 (rightmost contiguous seats after A5 is booked)
        assert assigned_seats == ["A6", "A7"]

def test_default_seating_advanced_with_existing_random_groups():
    from src.movie_classes import Booking
    movie = create_movie("Inception 2 6")  # Rows: A, B; Seats: 1-6
    # Existing bookings: A2, A3, A4 (middle block taken)
    movie.bookings = [
        Booking("GIC0001", "B", ["A2", "A3", "A4"])
    ]
    with patch.object(builtins, 'input', lambda *a, **k: ""):
        # New booking for 2 seats should get A5, A6
        movie = book_ticket_advanced(movie, 2)
        assert movie.bookings[-1].seats == ["A5", "A6"]
        # New booking for 2 seats should get B3, B4 as it is the next best contiguous block of seats for two people
        movie = book_ticket_advanced(movie, 2)
        assigned_seats2 = movie.bookings[-1].seats
        assert assigned_seats2 == ["B3", "B4"]  # B3, B4 are the most middle in B

def test_advanced_custom_seating_full_row():
    # Inception 3 5, row A fully booked, user input B3 for 5 seats
    movie = create_movie("Inception 3 5")
    # Book all seats in row A
    movie.bookings = [Booking("GIC0001", "B", [f"A{i}" for i in range(1, 6)])]
    assigned = advanced_custom_seating(movie, 5, "B3")
    # Should assign all of row B
    assert set(assigned) == {f"B{i}" for i in range(1, 6)}

def test_advanced_custom_seating_overflow_next_row():
    # Inception 3 5, row A fully booked, C3 booked, user input B5 for 7 seats
    movie = create_movie("Inception 3 5")
    # Book all seats in row A and C3
    movie.bookings = [
        Booking("GIC0001", "B", [f"A{i}" for i in range(1, 6)]),
        Booking("GIC0002", "B", ["C3"])
    ]
    assigned = advanced_custom_seating(movie, 7, "B5")
    # Should assign all of row B and C4, C5
    assert set(assigned) == {f"B{i}" for i in range(1, 6)} | {"C4", "C5"}

def test_advanced_custom_seating_large_movie_large_group():
    # Inception 10 20, book 18 seats starting at D10, some seats in D and E are booked
    movie = create_movie("Inception 10 20")
    # Book D5-D9, E1-E3, E18-E20
    movie.bookings = [
        Booking("GIC0001", "B", [f"D{i}" for i in range(5, 10)]),
        Booking("GIC0002", "B", [f"E{i}" for i in range(1, 4)] + [f"E{i}" for i in range(18, 21)])
    ]
    assigned = advanced_custom_seating(movie, 18, "D10")
    # Should fill D10-D20 (11 seats), then E11, E10, E12, E9, E13, E8, E14 (7 seats, most central with rightmost tie-breaker)
    expected = {f"D{i}" for i in range(10, 21)} | {"E11", "E10", "E12", "E9", "E13", "E8", "E14"}
    assert set(assigned) == expected

def test_advanced_custom_seating_small_movie_small_group():
    # Inception 2 3, book 2 seats starting at B2, all seats free
    movie = create_movie("Inception 2 3")
    assigned = advanced_custom_seating(movie, 2, "B2")
    # Should assign B2, B3 (rightmost contiguous)
    assert set(assigned) == {"B2", "B3"}

def test_advanced_custom_seating_fallback_noncontiguous():
    # Inception 2 3, book 3 seats starting at B2, but only B2 and A1, A3 are free
    movie = create_movie("Inception 2 3")
    # Book all except B2, A1, A3
    movie.bookings = [
        Booking("GIC0001", "B", ["A2", "B1", "B3"])
    ]
    assigned = advanced_custom_seating(movie, 3, "B2")
    # Should assign B2, A1, A3 (fallback to non-contiguous)
    assert set(assigned) == {"B2", "A1", "A3"}

def test_assign_from_starting_seat_basic():
    seat_map = {'A': [f'A{i}' for i in range(1, 6)]}
    booked = set()
    # Start at A3, want 3 seats
    result = assign_from_starting_seat(seat_map, booked, 'A', 3, 3)
    assert set(result) == {'A2', 'A3', 'A4'}

def test_assign_from_starting_seat_with_booked():
    seat_map = {'A': [f'A{i}' for i in range(1, 6)]}
    booked = {'A3'}
    result = assign_from_starting_seat(seat_map, booked, 'A', 2, 2)
    # Should return any pair containing A2 and one other available seat
    assert 'A2' in result and len(result) == 2 and all(seat in {'A1','A2','A4','A5'} for seat in result)

def test_find_best_subblock_central():
    blocks = [['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']]
    # Should pick A3-A5 as most central block of 3 in 7 seats
    result = find_best_subblock(blocks, 3, 7)
    assert result == ['A3', 'A4', 'A5']

def test_assign_overflow_rows_basic():
    seat_map = {'A': [f'A{i}' for i in range(1, 6)], 'B': [f'B{i}' for i in range(1, 6)]}
    booked = {'A1', 'A2', 'A3', 'A4', 'A5'}
    assigned = []
    row_letters = ['A', 'B']
    row_idx = 0
    seats_needed = 3
    seats_per_row = 5
    assigned, seats_needed = assign_overflow_rows(seat_map, booked, assigned, row_letters, row_idx, seats_needed, seats_per_row)
    assert set(assigned) == {'B2', 'B3', 'B4'}
    assert seats_needed == 0

def test_assign_fallback_seats():
    seat_map = {'A': ['A1', 'A2'], 'B': ['B1', 'B2']}
    booked = {'A1', 'B1'}
    assigned = []
    row_letters = ['A', 'B']
    seats_needed = 2
    result = assign_fallback_seats(seat_map, booked, assigned, row_letters, seats_needed)
    assert set(result) == {'A2', 'B2'}

def test_find_contiguous_blocks_basic():
    available = ['A1', 'A2', 'A4', 'A5', 'A6', 'A8']
    # Should find [A1, A2], [A4, A5, A6], [A8]
    result = find_contiguous_blocks(available)
    assert result == [['A1', 'A2'], ['A4', 'A5', 'A6'], ['A8']]

def test_find_contiguous_blocks_single():
    available = ['B3']
    result = find_contiguous_blocks(available)
    assert result == [['B3']]

def test_find_contiguous_blocks_empty():
    available = []
    result = find_contiguous_blocks(available)
    assert result == []

# Direct test for assign_single_seat_advanced (strict coverage)
def test_assign_single_seat_advanced():
    from src.booking_advanced import assign_single_seat_advanced
    # Case 1: All seats free
    rows = 2
    seats_per_row = 4
    seat_map = {'A': ['A1', 'A2', 'A3', 'A4'], 'B': ['B1', 'B2', 'B3', 'B4']}
    booked = set()
    assigned = []
    result = assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row)
    # Should pick the most central/rightmost seat (A3 or A2 for 4 seats, rightmost is A3)
    assert result == ['A3']

    # Case 2: Some seats booked/assigned
    booked = {'A3', 'A2', 'A4', 'B2', 'B3', 'B4'}
    assigned = []
    result = assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row)
    # Only A1 and B1 are free, row A takes priority so A1 is chosen
    assert result == ['A1']

    # Case 3: All seats booked/assigned
    booked = {'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'}
    assigned = []
    result = assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row)
    assert result == []

    # Case 4: Some seats already assigned (not booked)
    booked = set()
    assigned = ['A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4']
    result = assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row)
    # Only A1 is free
    assert result == ['A1']