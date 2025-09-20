import string
import copy
from src.movie import save_movie

def book_ticket(movie_json, num_tickets):
    """
    Adds a booking to the movie's bookings array.
    Uses get_booking_id to generate the next booking ID and assigns seats.
    Returns the modified movie JSON.
    """
    print(f"\nSuccessfully reserved {num_tickets} {movie_json['title']} tickets")
    booking_id = get_booking_id(movie_json)
    booking = {
            "ID": booking_id,
            "status": "R", # set as Reserved by default, will be set to B once user confirms
            "seats": []
        }
    # Ensure bookings is a list
    if "bookings" not in movie_json or not isinstance(movie_json["bookings"], list):
        movie_json["bookings"] = []
    
    # Assign seats using default_seating (now returns seat list)
    assigned_seats = default_seating(movie_json, num_tickets)
    booking["seats"] = assigned_seats
    
    movie_json["bookings"].append(booking)
    while True:
        print(f"\nBooking ID: {booking_id}")
        # here we will call the display function
        seating_input = input("\nEnter blank to accept seat selection, or enter new seating position:\n")
        if seating_input.strip() == "":
            movie_json = confirm_reservation(movie_json, booking_id)
            save_movie(movie_json)  # Save the updated movie JSON
            break
        else:
            print("Seat selection modification not yet implemented. Please enter blank to accept.")
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

def confirm_reservation(movie_json, booking_id):
    """
    Sets the status of the booking with the given ID to 'B' (booked) instead of default 'R' (reserved).
    This isn't strictly required per requirements but would prove useful for future extensions.
    Returns a modified copy of the movie JSON.
    """
    updated_movie = copy.deepcopy(movie_json)
    for booking in updated_movie.get("bookings", []):
        if booking.get("ID") == booking_id:
            booking["status"] = "B"
    return updated_movie

def build_seat_map(movie_json):
    """
    Build a dictionary mapping row letters to lists of seat labels for the movie.
    Example: {'A': ['A1', 'A2', ...], 'B': [...], ...}
    """
    rows = movie_json["row"]
    seats_per_row = movie_json["seats_per_row"]
    seat_map = {}
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        seat_map[row_letter] = [f"{row_letter}{n+1}" for n in range(seats_per_row)]
    return seat_map

def get_booked_seats(movie_json):
    """
    Return a set of all seat labels that are already booked or reserved in the movie.
    """
    booked = set()
    for booking in movie_json.get("bookings", []):
        for seat in booking.get("seats", []):
            booked.add(seat)
    return booked

def get_row_center(seats_per_row):
    """
    Returns the center seat number for a given number of seats per row.
    For even numbers, returns seats_per_row // 2.
    For odd numbers, returns (seats_per_row + 1) // 2.
    """
    if seats_per_row % 2 == 0:
        return seats_per_row // 2
    else:
        return (seats_per_row + 1) // 2

def ordered_free_seat_map(seat_map, booked):
    """
    Returns a list of available seats ordered by centrality (most central first, rightmost in tie), row by row (front to back).
    Booked seats are excluded.
    """
    result = []
    row_letters = sorted(seat_map.keys())
    for row_letter in row_letters:
        seats = [s for s in seat_map[row_letter] if s not in booked]
        seats_per_row = len(seat_map[row_letter])
        # Use seat_sort_order to order by centrality, rightmost in tie
        ordered = seat_sort_order(seats, seats_per_row)
        result.extend(ordered)
    return result

def seat_sort_order(seats, seats_per_row, take=None):
    """
    Given a list of seat labels (e.g., ["A1", "A2", ...]), return them ordered by centrality.
    If take is provided, return only the most central N seats.
    """
    if not seats:
        return []
    seat_tuples = []
    for s in seats:
        seat_num = int(s[1:])
        if seats_per_row % 2 == 0:
            center_left = seats_per_row // 2
            center_right = center_left + 1
            if seat_num == center_left or seat_num == center_right:
                dist = 0
                tiebreak = -seat_num
            else:
                center_val = seats_per_row / 2 + 0.5
                dist = abs(seat_num - center_val)
                tiebreak = -seat_num
            seat_tuples.append((dist, tiebreak, s))
        else:
            center_val = (seats_per_row + 1) // 2
            dist = abs(seat_num - center_val)
            seat_tuples.append((dist, -seat_num, s))
    seat_tuples.sort()
    result = [t[2] for t in seat_tuples]
    if take:
        result = result[:take]
    return result

def default_seating(movie_json, num_tickets):
    """
    Assign the best available  seats for the given group size.
    - Fills from row A (back) to front row.
    - Picks the most middle seats available in a row.
    - Skips already booked seats.
    Returns a list of assigned seat labels.
    """

    seat_map = build_seat_map(movie_json)
    booked = get_booked_seats(movie_json)
    ordered_seats = ordered_free_seat_map(seat_map, booked)
    # Assign up to num_tickets seats from the ordered list
    return ordered_seats[:num_tickets]


