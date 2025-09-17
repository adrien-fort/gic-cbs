from src.movie import create_movie

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
