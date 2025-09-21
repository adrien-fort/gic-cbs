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
    Returns True if user_input is not booked (status 'B').
    Reserved (status 'R') and unoccupied seats are valid.
    """
    # Check if seat exists in the seat map
    rows = movie_json["row"]
    seats_per_row = movie_json["seats_per_row"]
    seat_map = {}
    import string
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        seat_map[row_letter] = [f"{row_letter}{n+1}" for n in range(seats_per_row)]
    # Validate seat exists in map
    found = False
    for row_seats in seat_map.values():
        if user_input in row_seats:
            found = True
            break
    if not found:
        return False
    # Check bookings for status B
    for booking in movie_json.get("bookings", []):
        if booking.get("status") == "B" and user_input in booking.get("seats", []):
            return False
    return True

