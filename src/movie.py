"""
movie.py
--------
This module contains functions related to movie creation and management.
"""

def create_movie(user_input):
    """
    Takes validated user input (string) and returns a JSON-serializable dict representing the movie theatre.
    The JSON output include an empty array for bookings that will be filled by other functions.
    """
    parts = user_input.strip().split()
    title = " ".join(parts[:-2])
    row = int(parts[-2])
    seats_per_row = int(parts[-1])
    return {
        "title": title,
        "row": row,
        "seats_per_row": seats_per_row,
        "bookings": []  # Each booking: {"ID": ..., "status": ..., "seats": ...}
    }

def movie_available_seats(movie):
    """
    Returns the number of available seats for the given movie JSON.
    For now, simply returns row * seats_per_row (no bookings considered).
    """
    return movie["row"] * movie["seats_per_row"]

def save_movie(movie_json):
    """
    Saves the movie JSON object to logs/movie.json, overwriting if it exists.
    This functionality is not explicitely requested in the requirements but is useful for both debugging and future enhancements.
    """
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
    Returns a string representing the seating chart for the movie, showing reserved seats as 'o'.
    """
    rows = movie["row"]
    seats_per_row = movie["seats_per_row"]
    seat_map = {chr(ord('A') + i): ['.'] * seats_per_row for i in range(rows)}
    # Mark reserved seats as 'o'
    for booking in movie.get("bookings", []):
        if booking.get("status") == "R":
            for seat in booking.get("seats", []):
                row = seat[0]
                num = int(seat[1:]) - 1
                seat_map[row][num] = 'o'
    # Build display
    lines = []
    lines.append("    S C R E E N")
    lines.append("-" * 30)
    for i in range(rows-1, -1, -1):
        row_letter = chr(ord('A') + i)
        row_str = row_letter + ' ' + ' '.join(seat_map[row_letter])
        lines.append(row_str)
    # Footer with seat numbers
    footer = '  ' + ' '.join(str(n+1) for n in range(seats_per_row))
    lines.append(footer)
    return '\n'.join(lines)