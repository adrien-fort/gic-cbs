
"""
validation.py
-------------
This module contains validation functions for the GIC CBS application.
"""

from src.logger import log_info, log_warning, log_error

def is_positive_integer(value):
    log_info(f"Validating if value is positive integer: {value}")
    """Return True if value is a positive integer, False otherwise."""
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False

def movie_validation(user_input):
    log_info(f"Validating movie input: '{user_input}'")
    """
    Validate input in the format: [Title] [Row] [SeatsPerRow]
    - Title: non-empty string (can contain spaces, but must be first)
    - Row: positive integer maximum 26
    - SeatsPerRow: positive integer maximum 50
    Returns True if valid, False otherwise.
    """
    if not isinstance(user_input, str):
        log_warning("Movie input is not a string.")
        return False
    parts = user_input.strip().split()
    if len(parts) < 3:
        log_warning("Movie input does not have at least 3 parts.")
        return False
    # Title can be multiple words, so join all but last two as title
    title = " ".join(parts[:-2])
    row = parts[-2]
    seats_per_row = parts[-1]
    if not title.strip():
        log_warning("Movie title is empty.")
        return False
    if not is_positive_integer(row):
        log_warning("Row is not a positive integer.")
        return False
    if not is_positive_integer(seats_per_row):
        log_warning("Seats per row is not a positive integer.")
        return False
    row_int = int(row)
    seats_int = int(seats_per_row)
    if not (1 <= row_int <= 26):
        log_warning("Row is out of allowed range (1-26).")
        return False
    if not (1 <= seats_int <= 50):
        log_warning("Seats per row is out of allowed range (1-50).")
        return False
    log_info("Movie input validated successfully.")
    return True

def ticket_num_validation(ticket_input, movie_json):
    log_info(f"Validating ticket number: {ticket_input}")
    """
    Returns True if ticket_input is a positive integer and less than or equal to available seats in the movie.
    """
    from src.movie import movie_available_seats
    try:
        num = int(ticket_input)
        if num <= 0:
            log_warning("Ticket number is not positive.")
            return False
    except (ValueError, TypeError):
        log_warning("Ticket input is not a valid integer.")
        return False
    available = movie_available_seats(movie_json)
    if num > available:
        log_warning(f"Requested tickets ({num}) exceed available seats ({available}).")
        return False
    log_info("Ticket number validated successfully.")
    return True

def is_valid_seat(movie_json, user_input):
    log_info(f"Validating seat input: '{user_input}'")
    """
    Returns 'blank' if input is blank (accept default), 'valid' if seat is valid and available, 'invalid' otherwise.
    """
    from src.booking import build_seat_map, get_booked_seats
    if user_input.strip() == "":
        log_info("Seat input is blank (accept default)."); return "blank"
    seat_input = user_input.upper()
    seat_map = build_seat_map(movie_json)
    row = seat_input[0]
    try:
        int(seat_input[1:])
    except (ValueError, IndexError):
        log_warning("Seat input does not have a valid seat number."); return "invalid"
    if row not in seat_map:
        log_warning(f"Row '{row}' not in seat map."); return "invalid"
    if seat_input not in seat_map[row]:
        log_warning(f"Seat '{seat_input}' not in row '{row}'."); return "invalid"
    booked = get_booked_seats(movie_json)
    if seat_input in booked:
        log_warning(f"Seat '{seat_input}' is already booked."); return "invalid"
    log_info(f"Seat '{seat_input}' is valid and available.")
    return "valid"

def is_valid_booking(movie_json, booking_id):
    """
    Returns True if booking_id exists in the movie's bookings, False otherwise.
    Handles invalid or non-string IDs gracefully.
    """
    log_info(f"Validating booking ID: {booking_id}")
    if not isinstance(movie_json, dict) or "bookings" not in movie_json:
        log_warning("movie_json is not valid or missing 'bookings'.")
        return False
    if not isinstance(booking_id, str):
        log_warning("Booking ID is not a string.")
        return False
    for booking in movie_json["bookings"]:
        if booking.get("ID") == booking_id:
            log_info(f"Booking ID '{booking_id}' found.")
            return True
    log_info(f"Booking ID '{booking_id}' not found.")
    return False
