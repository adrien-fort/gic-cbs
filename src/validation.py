"""
validation.py
-------------
This module contains validation functions for the GIC CBS application.
"""

def is_positive_integer(value):
    """Return True if value is a positive integer, False otherwise."""
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False

def movie_validation(user_input):
    """
    Validate input in the format: [Title] [Row] [SeatsPerRow]
    - Title: non-empty string (can contain spaces, but must be first)
    - Row: positive integer maximum 26
    - SeatsPerRow: positive integer maximum 50
    Returns True if valid, False otherwise.
    """
    if not isinstance(user_input, str):
        return False
    parts = user_input.strip().split()
    if len(parts) < 3:
        return False
    # Title can be multiple words, so join all but last two as title
    title = " ".join(parts[:-2])
    row = parts[-2]
    seats_per_row = parts[-1]
    if not title.strip():
        return False
    if not is_positive_integer(row):
        return False
    if not is_positive_integer(seats_per_row):
        return False
    row_int = int(row)
    seats_int = int(seats_per_row)
    if not (1 <= row_int <= 26):
        return False
    if not (1 <= seats_int <= 50):
        return False
    return True

def ticket_num_validation(ticket_input, movie_json):
    """
    Returns True if ticket_input is a positive integer and less than or equal to available seats in the movie.
    """
    from src.movie import movie_available_seats
    try:
        num = int(ticket_input)
        if num <= 0:
            return False
    except (ValueError, TypeError):
        return False
    available = movie_available_seats(movie_json)
    return num <= available

def is_valid_seat(movie_json, user_input):
    """
    Returns 'blank' if input is blank (accept default), 'valid' if seat is valid and available, 'invalid' otherwise.
    """
    from src.booking import build_seat_map, get_booked_seats
    if user_input.strip() == "":
        return "blank"
    seat_input = user_input.upper()
    seat_map = build_seat_map(movie_json)
    row = seat_input[0]
    try:
        int(seat_input[1:])
    except (ValueError, IndexError):
        return "invalid"
    if row not in seat_map:
        return "invalid"
    if seat_input not in seat_map[row]:
        return "invalid"
    booked = get_booked_seats(movie_json)
    if seat_input in booked:
        return "invalid"
    return "valid"

