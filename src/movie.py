
"""
movie.py
--------
This module contains functions related to movie creation and management.
"""


from src.logger import log_info, log_warning, log_error
from src.movie_classes import Movie, Booking

def create_movie(user_input):
    """
    Create a Movie instance from user input string.
    Args:
        user_input (str): Input in the format '[Title] [Row] [SeatsPerRow]'.
    Returns:
        Movie: The created Movie instance.
    """
    log_info(f"Creating movie with input: '{user_input}'")
    parts = user_input.strip().split()
    title = " ".join(parts[:-2])
    row = int(parts[-2])
    seats_per_row = int(parts[-1])
    return Movie(title, row, seats_per_row)

def movie_available_seats(movie: Movie):
    """
    Calculate the number of available (unbooked) seats for a Movie instance.
    Args:
        movie (Movie): The Movie instance.
    Returns:
        int: Number of available seats.
    """
    log_info(f"Calculating available seats for movie: {getattr(movie, 'title', 'Unknown')}")
    total = movie.row * movie.seats_per_row
    booked = 0
    for booking in movie.bookings:
        booked += len(booking.seats)
    return total - booked

def save_movie(movie):
    """
    Save a Movie instance (or dict) to a JSON file in the logs directory.
    Args:
        movie (Movie or dict): The Movie instance or dict to save.
    """
    if isinstance(movie, Movie):
        movie_json = movie.to_dict()
        title = movie.title
    else:
        movie_json = movie
        title = movie.get('title', 'Unknown')
    log_info(f"Saving movie JSON for '{title}' to logs/movie.json")
    import os
    import json
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    movie_file = os.path.join(log_dir, 'movie.json')
    with open(movie_file, 'w') as f:
        json.dump(movie_json, f)

def movie_display(movie):
    """
    Build a string representation of the movie seating chart for display.
    Args:
        movie (Movie or dict): The Movie instance or dict.
    Returns:
        str: The formatted seating chart as a string.
    """
    if isinstance(movie, Movie):
        rows = movie.row
        seats_per_row = movie.seats_per_row
        seat_map = build_seat_display_map(movie)
        title = movie.title
    else:
        rows = movie["row"]
        seats_per_row = movie["seats_per_row"]
        seat_map = build_seat_display_map(movie)
        title = movie.get('title', 'Unknown')
    log_info(f"Building display for movie: {title}")
    lines = []
    lines.append("Selected seats:\n")
    screen_text = "S C R E E N"
    if seats_per_row > 10:
        total_width = seats_per_row * 3 + 1
    else:
        total_width = seats_per_row * 2 + 2
    screen_centered = screen_text.center(total_width)
    lines.append(screen_centered)
    lines.append("-" * total_width)
    seat_sep = '  ' if seats_per_row > 10 else ' '
    for i in range(rows-1, -1, -1):
        row_letter = chr(ord('A') + i)
        row_str = row_letter + ' ' + seat_sep.join(seat_map[row_letter])
        lines.append(row_str)
    footer = '  '
    for n in range(1, seats_per_row + 1):
        if n < 10 and seats_per_row > 10:
            footer += str(n) + '  '
        else:
            footer += str(n) + ' '
    lines.append(footer.rstrip())
    return '\n'.join(lines)

def mark_seats_on_map(seat_map, status, seats):
    """
    Mark the given seats on the seat_map with the appropriate symbol based on status.
    'R' (reserved) -> 'o', 'B' (booked) -> '#'.
    Args:
        seat_map (dict): The seat map to modify.
        status (str): The booking status ('R' or 'B').
        seats (list): List of seat labels to mark.
    """
    if status == "R":
        for seat in seats:
            row = seat[0]
            num = int(seat[1:]) - 1
            seat_map[row][num] = 'o'
    if status == "B":
        for seat in seats:
            row = seat[0]
            num = int(seat[1:]) - 1
            seat_map[row][num] = '#'

def build_seat_display_map(movie):
    """
    Build a seat map for display, marking reserved and booked seats with symbols.
    Args:
        movie (Movie or dict): The Movie instance or dict.
    Returns:
        dict: Seat map with symbols for display.
    """
    if isinstance(movie, Movie):
        rows = movie.row
        seats_per_row = movie.seats_per_row
        bookings = movie.bookings
        title = movie.title
    else:
        rows = movie["row"]
        seats_per_row = movie["seats_per_row"]
        bookings = movie.get("bookings", [])
        title = movie.get('title', 'Unknown')
    log_info(f"Building seat display map for movie: {title}")
    seat_map = {chr(ord('A') + i): ['.'] * seats_per_row for i in range(rows)}
    for booking in bookings:
        status = booking.status if isinstance(booking, Booking) else booking.get("status")
        seats = booking.seats if isinstance(booking, Booking) else booking.get("seats", [])
        mark_seats_on_map(seat_map, status, seats)
    return seat_map