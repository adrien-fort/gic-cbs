"""
test_movie.py
------------
Unit tests for the movie module, covering movie creation, seat availability, and display logic.
"""

from src.movie import create_movie, movie_available_seats, movie_display, build_seat_display_map
import os
import json

def test_movie_display_basic():
    movie = create_movie("Inception 8 10")
    # Insert a reserved booking for A4, A5, A6, A7
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "R",
        "seats": ["A4", "A5", "A6", "A7"]
    })
    output = movie_display(movie)
    expected = (
        "Selected seats:\n"
        "\n"
        "     S C R E E N      \n"
        "----------------------\n"
        "H . . . . . . . . . .\n"
        "G . . . . . . . . . .\n"
        "F . . . . . . . . . .\n"
        "E . . . . . . . . . .\n"
        "D . . . . . . . . . .\n"
        "C . . . . . . . . . .\n"
        "B . . . . . . . . . .\n"
        "A . . . o o o o . . .\n"
        "  1 2 3 4 5 6 7 8 9 10"
    )
    assert output.strip() == expected.strip()


def test_movie_display_booked():
    movie = create_movie("Inception 2 4")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "B",
        "seats": ["A1", "B3"]
    })
    output = movie_display(movie)
    expected = (
        "Selected seats:\n"
        "\n"
        "S C R E E N\n"
        "----------\n"
        "B . . # .\n"
        "A # . . .\n"
        "  1 2 3 4"
    )
    assert output.strip() == expected.strip()


def test_movie_display_mixed():
    movie = create_movie("Inception 2 4")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "R",
        "seats": ["A2"]
    })
    movie["bookings"].append({
        "ID": "GIC0002",
        "status": "B",
        "seats": ["A1", "B3"]
    })
    output = movie_display(movie)
    expected = (
        "Selected seats:\n"
        "\n"
        "S C R E E N\n"
        "----------\n"
        "B . . # .\n"
        "A # o . .\n"
        "  1 2 3 4"
    )
    assert output.strip() == expected.strip()


def test_movie_display_wide():
    movie = create_movie("Inception 1 12")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "B",
        "seats": ["A1", "A12"]
    })
    output = movie_display(movie)
    expected = (
        "Selected seats:\n"
        "\n"
        "             S C R E E N             \n"
        "-------------------------------------\n"
        "A #  .  .  .  .  .  .  .  .  .  .  #\n"
        "  1  2  3  4  5  6  7  8  9  10 11 12"
    )
    assert output.strip() == expected.strip()


def test_create_movie_basic():
    user_input = "Inception 8 10"
    movie = create_movie(user_input)
    assert movie["title"] == "Inception"
    assert movie["row"] == 8
    assert movie["seats_per_row"] == 10
    assert isinstance(movie["bookings"], list)
    assert movie["bookings"] == []


def test_create_movie_multiword_title():
    user_input = "Die Hard 2 16 45"
    movie = create_movie(user_input)
    assert movie["title"] == "Die Hard 2"
    assert movie["row"] == 16
    assert movie["seats_per_row"] == 45
    assert isinstance(movie["bookings"], list)
    assert movie["bookings"] == []


def test_create_movie_json_structure():
    user_input = "Avatar 12 50"
    movie = create_movie(user_input)
    # Check all required keys
    for key in ["title", "row", "seats_per_row", "bookings"]:
        assert key in movie
    # Check bookings is a list and empty
    assert isinstance(movie["bookings"], list)
    assert len(movie["bookings"]) == 0


def test_movie_available_seats_no_bookings():
    movie = create_movie("Inception 8 10")
    assert movie_available_seats(movie) == 80


def test_movie_available_seats_with_bookings():
    movie = create_movie("Inception 8 10")
    # Book A6, A5, A7, A4
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "B",
        "seats": ["A6", "A5", "A7", "A4"]
    })
    assert movie_available_seats(movie) == 76


def test_save_movie_creates_and_overwrites_file():
    from src.movie import save_movie
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    movie_file = os.path.join(logs_dir, 'movie.json')

    # Ensure clean state
    if os.path.exists(movie_file):
        os.remove(movie_file)

    movie1 = create_movie("Inception 8 10")
    save_movie(movie1)
    assert os.path.exists(movie_file)
    with open(movie_file, 'r') as f:
        data = json.load(f)
    assert data == movie1

    # Overwrite with different movie
    movie2 = create_movie("Avatar 12 50")
    save_movie(movie2)
    with open(movie_file, 'r') as f:
        data2 = json.load(f)
    assert data2 == movie2


def test_build_seat_display_map_empty():
    movie = create_movie("Inception 3 5")
    seat_map = build_seat_display_map(movie)
    assert seat_map == {
        'A': ['.', '.', '.', '.', '.'],
        'B': ['.', '.', '.', '.', '.'],
        'C': ['.', '.', '.', '.', '.']
    }

def test_build_seat_display_map_reserved():
    movie = create_movie("Inception 2 4")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "R",
        "seats": ["A2", "B4"]
    })
    seat_map = build_seat_display_map(movie)
    assert seat_map == {
        'A': ['.', 'o', '.', '.'],
        'B': ['.', '.', '.', 'o']
    }

def test_build_seat_display_map_booked():
    movie = create_movie("Inception 2 4")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "B",
        "seats": ["A1", "B3"]
    })
    seat_map = build_seat_display_map(movie)
    assert seat_map == {
        'A': ['#', '.', '.', '.'],
        'B': ['.', '.', '#', '.']
    }

def test_build_seat_display_map_mixed():
    movie = create_movie("Inception 2 4")
    movie["bookings"].append({
        "ID": "GIC0001",
        "status": "R",
        "seats": ["A2"]
    })
    movie["bookings"].append({
        "ID": "GIC0002",
        "status": "B",
        "seats": ["A1", "B3"]
    })
    seat_map = build_seat_display_map(movie)
    assert seat_map == {
        'A': ['#', 'o', '.', '.'],
        'B': ['.', '.', '#', '.']
    }
