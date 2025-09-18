from src.movie import create_movie, movie_available_seats
import os
import json

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
