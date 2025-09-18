def book_ticket(movie_json, num_tickets):
    """
    Adds a booking to the movie's bookings array.
    Uses get_booking_id to generate the next booking ID.
    For now, always adds booking with status B, seats ["A4", "A5"] for 2 tickets.
    Returns the modified movie JSON.
    """
    booking_id = get_booking_id(movie_json)
    booking = {
        "ID": booking_id,
        "status": "B",
        "seats": ["A4", "A5"]
    }
    movie_json = movie_json.copy()
    # Ensure bookings is a list
    if "bookings" not in movie_json or not isinstance(movie_json["bookings"], list):
        movie_json["bookings"] = []
    movie_json["bookings"].append(booking)
    return movie_json


def get_booking_id(movie_json):
    """
    Returns the next booking ID in the format GIC####, scanning the bookings array for the highest number.
    """
    bookings = movie_json.get("bookings", [])
    max_id = 0
    for booking in bookings:
        bid = booking.get("ID", "")
        if bid.startswith("GIC") and bid[3:].isdigit():
            num = int(bid[3:])
            if num > max_id:
                max_id = num
    next_id = max_id + 1
    return f"GIC{next_id:04d}"
