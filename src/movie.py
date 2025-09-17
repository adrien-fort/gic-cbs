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
