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
    Subtracts the number of booked seats from the total.
    """
    total = movie["row"] * movie["seats_per_row"]
    booked = 0
    for booking in movie.get("bookings", []):
        booked += len(booking.get("seats", []))
    return total - booked

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
    Returns a string representing the seating chart for the movie. 
    Showing reserved seats as 'o' and booked seats as '#'.
    The spacing adjusts for double-digit seat numbers.
    """
    rows = movie["row"]
    seats_per_row = movie["seats_per_row"]
    seat_map = build_seat_display_map(movie)
    # Build display
    lines = []
    lines.append("Selected seats:\n")
    # Calculate width for centering
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
    # Footer with seat numbers
    footer = '  '
    for n in range(1, seats_per_row + 1):
        if n < 10:
            footer += str(n) + '  '
        else:
            footer += str(n) + ' '
    lines.append(footer.rstrip())
    return '\n'.join(lines)

def build_seat_display_map(movie):
    """
    Returns a seat map for display, marking reserved seats as 'o' and booked seats as '#'.
    """
    rows = movie["row"]
    seats_per_row = movie["seats_per_row"]
    seat_map = {chr(ord('A') + i): ['.'] * seats_per_row for i in range(rows)}
    for booking in movie.get("bookings", []):
        if booking.get("status") == "R":
            for seat in booking.get("seats", []):
                row = seat[0]
                num = int(seat[1:]) - 1
                seat_map[row][num] = 'o'
        if booking.get("status") == "B":
            for seat in booking.get("seats", []):
                row = seat[0]
                num = int(seat[1:]) - 1
                seat_map[row][num] = '#'
    return seat_map