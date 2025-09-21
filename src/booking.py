from src.logger import log_info, log_warning, log_error
import string
from src.movie import save_movie, movie_display
from src.validation import is_valid_seat
"""
Booking.py
--------
This module contains functions related to movie booking the book_ticket function drives the flow.
The two main approaches to seating are default_seating (best available) and custom_seating (user selected).
"""

def book_ticket(movie_json, num_tickets):
    """
    Adds a booking to the movie's bookings array.
    Uses get_booking_id to generate the next booking ID and assigns seats.
    Returns the modified movie JSON.
    """
    log_info(f"Starting booking for {num_tickets} tickets for movie '{movie_json['title']}'")
    print(f"\nSuccessfully reserved {num_tickets} {movie_json['title']} tickets.")
    booking_id = get_booking_id(movie_json)
    log_info(f"Generated booking ID: {booking_id}")
    booking = {
        "ID": booking_id,
        "status": "R", # set as Reserved by default, will be set to B once user confirms
        "seats": []
    }
    # Ensure bookings is a list
    if "bookings" not in movie_json or not isinstance(movie_json["bookings"], list):
        log_warning("'bookings' key missing or not a list in movie_json. Initializing new list.")
        movie_json["bookings"] = []
    
    # Assign seats using default_seating (now returns seat list)
    assigned_seats = default_seating(movie_json, num_tickets)
    booking["seats"] = assigned_seats
    log_info(f"Default seats assigned: {assigned_seats}")
    
    movie_json["bookings"].append(booking)
    log_info(f"Booking object added to movie_json: {booking}")
    save_movie(movie_json)  # Save the updated movie JSON
    log_info("Initial booking saved to movie file.")
    while True:
        print(f"\nBooking ID: {booking_id}")
        print(movie_display(movie_json))
        seating_input = input("\nEnter blank to accept seat selection, or enter new seating position:\n> ")
        status = is_valid_seat(movie_json, seating_input)
        if status == "blank":
            log_info(f"Booking {booking_id} confirmed by user.")
            movie_json = confirm_reservation(movie_json, booking_id)
            save_movie(movie_json)  # Save the updated movie JSON
            log_info(f"Booking {booking_id} status set to 'B' and saved.")
            print(f"\nBooking ID: {booking_id} confirmed.\n")
            break
        elif status == "valid":
            assigned_seats = custom_seating(movie_json, num_tickets, seating_input.strip().upper())
            log_info(f"Custom seating input '{seating_input.strip().upper()}' accepted. Seats assigned: {assigned_seats}")
            for b in movie_json["bookings"]:
                if b["ID"] == booking_id:
                    b["seats"] = assigned_seats
                    break
            save_movie(movie_json)  # Save the updated movie JSON
            log_info(f"Booking {booking_id} updated with custom seats and saved.")
        else:
            log_warning(f"Invalid seat input '{seating_input.strip()}'; prompt user again.")
            print(f"Seat {seating_input.strip()} is not valid. Please try again or enter blank to accept.")
    return movie_json

def get_booking_id(movie_json):
    log_info("Calculating next booking ID.")
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
    log_info(f"Confirming reservation for booking ID: {booking_id}")
    """
    Sets the status of the booking with the given ID to 'B' (booked) instead of default 'R' (reserved).
    Modifies the movie_json in place.
    """
    for booking in movie_json.get("bookings", []):
        if booking.get("ID") == booking_id:
            booking["status"] = "B"
    return movie_json

def build_seat_map(movie_json):
    log_info(f"Building seat map for movie: {movie_json.get('title', 'Unknown')}")
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
    log_info("Getting all booked seats for movie.")
    """
    Return a set of all seat labels that are already booked (status 'B') in the movie.
    Reserved (status 'R') seats are not considered booked for exclusion.
    """
    booked = set()
    for booking in movie_json.get("bookings", []):
        if booking.get("status") == "B":
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
    log_info(f"Assigning default seating for {num_tickets} tickets.")
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

def fill_right_in_row(row, start_num, seats_per_row, booked, assigned):
    """
    Fill seats to the right of the starting seat in the same row, skipping booked or already assigned seats.
    Returns a list of available seat labels.
    """
    filled = []
    for n in range(start_num, seats_per_row + 1):
        seat = f"{row}{n}"
        if seat not in booked and seat not in assigned and seat not in filled:
            filled.append(seat)
    return filled

def fill_next_rows_by_centrality(row_idx, row_letters, seat_map, seats_per_row, booked, assigned):
    """
    Fill seats in the next rows (forward), ordered by centrality, skipping booked or already assigned seats.
    Returns a list of available seat labels.
    """
    filled = []
    for next_row_idx in range(row_idx + 1, len(row_letters)):
        next_row = row_letters[next_row_idx]
        available = [s for s in seat_map[next_row] if s not in booked and s not in assigned and s not in filled]
        ordered = seat_sort_order(available, seats_per_row)
        filled.extend(ordered)
    return filled

def fill_left_in_row(row, start_num, booked, assigned):
    """
    Fill seats to the left of the starting seat in the same row, skipping booked or already assigned seats.
    Returns a list of available seat labels.
    """
    filled = []
    for n in range(start_num - 1, 0, -1):
        seat = f"{row}{n}"
        if seat not in booked and seat not in assigned and seat not in filled:
            filled.append(seat)
    return filled

def fill_prev_rows_by_centrality(row_idx, row_letters, seat_map, seats_per_row, booked, assigned):
    """
    Fill seats in the previous rows (backward), ordered by centrality, skipping booked or already assigned seats.
    Returns a list of available seat labels.
    """
    filled = []
    for prev_row_idx in range(row_idx - 1, -1, -1):
        prev_row = row_letters[prev_row_idx]
        available = [s for s in seat_map[prev_row] if s not in booked and s not in assigned and s not in filled]
        ordered = seat_sort_order(available, seats_per_row)
        filled.extend(ordered)
    return filled

def custom_seating(movie_json, num_tickets, seat_input):
    log_info(f"Assigning custom seating for {num_tickets} tickets starting at {seat_input}.")
    """
    Assigns seats starting from the user-selected seat, filling to the right in the same row.
    If not enough seats are available to the right, overflow to the next row(s) by centrality.
    Only if still not enough, fill left from the starting point in the original row.
    Returns a list of assigned seat labels.
    """
    seat_map = build_seat_map(movie_json)
    booked = get_booked_seats(movie_json)
    assigned = []
    row = seat_input[0]
    start_num = int(seat_input[1:])
    seats_per_row = movie_json["seats_per_row"]
    row_letters = list(seat_map.keys())
    row_idx = row_letters.index(row)

    # 1. Fill to the right in the same row
    right = fill_right_in_row(row, start_num, seats_per_row, booked, assigned)
    assigned.extend(right)
    if len(assigned) >= num_tickets:
        return assigned[:num_tickets]

    # 2. Fill next rows (forward), by centrality
    next_rows = fill_next_rows_by_centrality(row_idx, row_letters, seat_map, seats_per_row, booked, assigned)
    assigned.extend(next_rows)
    if len(assigned) >= num_tickets:
        return assigned[:num_tickets]

    # 3. Fill to the left in the original row
    left = fill_left_in_row(row, start_num, booked, assigned)
    assigned.extend(left)
    if len(assigned) >= num_tickets:
        return assigned[:num_tickets]

    # 4. Fill previous rows (backward), by centrality
    prev_rows = fill_prev_rows_by_centrality(row_idx, row_letters, seat_map, seats_per_row, booked, assigned)
    assigned.extend(prev_rows)
    return assigned[:num_tickets]


