

"""
booking.py
==========
This module contains functions related to movie booking. The book_ticket function drives the flow.
The two main approaches to seating are default_seating (best available) and custom_seating (user selected).
"""


from src.logger import log_info, log_warning, log_error
import string
from src.movie import save_movie, movie_display
from src.validation import is_valid_seat
from src.movie_classes import Movie, Booking

def book_ticket(movie: Movie, num_tickets):
    """
    Adds a new Booking object to the Movie's bookings list.
    Generates a booking ID, assigns default or custom seats, and saves the updated Movie.
    Handles user confirmation and seat selection loop, updating the booking as needed.
    Returns the updated Movie instance.
    """
    log_info(f"Starting booking for {num_tickets} tickets for movie '{movie.title}'")
    print(f"\nSuccessfully reserved {num_tickets} {movie.title} tickets.")
    booking_id = get_booking_id(movie)
    log_info(f"Generated booking ID: {booking_id}")

    booking = Booking(booking_id, "R", [])
    assigned_seats = default_seating(movie, num_tickets)
    booking.seats = assigned_seats
    log_info(f"Default seats assigned: {assigned_seats}")

    movie.add_booking(booking)
    log_info(f"Booking object added to movie: {booking.to_dict()}")
    save_movie(movie.to_dict())  # Save the updated movie
    log_info("Initial booking saved to movie file.")
    while True:
        print(f"\nBooking ID: {booking_id}")
        print(movie_display(movie.to_dict()))
        seating_input = input("\nEnter blank to accept seat selection, or enter new seating position:\n> ")
        status = is_valid_seat(movie, seating_input)
        if status == "blank":
            log_info(f"Booking {booking_id} confirmed by user.")
            confirm_reservation(movie, booking_id)
            save_movie(movie.to_dict())
            log_info(f"Booking {booking_id} status set to 'B' and saved.")
            print(f"\nBooking ID: {booking_id} confirmed.\n")
            break
        elif status == "valid":
            assigned_seats = custom_seating(movie, num_tickets, seating_input.strip().upper())
            log_info(f"Custom seating input '{seating_input.strip().upper()}' accepted. Seats assigned: {assigned_seats}")
            b = movie.get_booking(booking_id)
            if b:
                b.seats = assigned_seats
            save_movie(movie.to_dict())
            log_info(f"Booking {booking_id} updated with custom seats and saved.")
        else:
            log_warning(f"Invalid seat input '{seating_input.strip()}'; prompt user again.")
            print(f"Seat {seating_input.strip()} is not valid. Please try again or enter blank to accept.")
    return movie

def get_booking_id(movie: Movie):
    """
    Calculate the next available booking ID for a Movie instance.
    Booking IDs are in the format 'GIC0001', 'GIC0002', etc.
    Args:
        movie (Movie): The Movie instance to check existing bookings.
    Returns:
        str: The next booking ID string.
    """
    log_info("Calculating next booking ID.")
    max_id = 0
    for booking in movie.bookings:
        bid = booking.id
        if bid.startswith("GIC") and bid[3:].isdigit():
            num = int(bid[3:])
            if num > max_id:
                max_id = num
    next_id = max_id + 1
    return f"GIC{next_id:04d}"

def confirm_reservation(movie: Movie, booking_id):
    """
    Set the status of the booking with the given ID to 'B' (booked).
    Args:
        movie (Movie): The Movie instance containing the booking.
        booking_id (str): The booking ID to confirm.
    Returns:
        Movie: The updated Movie instance.
    """
    log_info(f"Confirming reservation for booking ID: {booking_id}")
    b = movie.get_booking(booking_id)
    if b:
        b.status = "B"
    return movie

def build_seat_map(movie: Movie):
    """
    Build a seat map for the given Movie instance.
    Returns a dict mapping row letters to lists of seat labels (e.g., {'A': ['A1', 'A2', ...]}).
    Args:
        movie (Movie): The Movie instance.
    Returns:
        dict: Seat map by row letter.
    """
    log_info(f"Building seat map for movie: {getattr(movie, 'title', 'Unknown')}")
    rows = movie.row
    seats_per_row = movie.seats_per_row
    seat_map = {}
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        seat_map[row_letter] = [f"{row_letter}{n+1}" for n in range(seats_per_row)]
    return seat_map

def get_booked_seats(movie: Movie):
    """
    Get all seats that are currently booked ('B') for a Movie instance.
    Args:
        movie (Movie): The Movie instance.
    Returns:
        set: Set of booked seat labels (e.g., {'A1', 'B2'}).
    """
    log_info("Getting all booked seats for movie.")
    booked = set()
    for booking in movie.bookings:
        if booking.status == "B":
            for seat in booking.seats:
                booked.add(seat)
    return booked

def get_row_center(seats_per_row):
    """
    Returns the center seat number for a given number of seats per row.
    For even numbers, returns seats_per_row // 2.
    For odd numbers, returns (seats_per_row + 1) // 2.
    Args:
        seats_per_row (int): Number of seats in the row.
    Returns:
        int: The center seat number.
    """
    if seats_per_row % 2 == 0:
        return seats_per_row // 2
    else:
        return (seats_per_row + 1) // 2

def ordered_free_seat_map(seat_map, booked):
    """
    Returns a list of available seats ordered by centrality (most central first, rightmost in tie), row by row (front to back).
    Booked seats are excluded.
    Args:
        seat_map (dict): Seat map by row letter.
        booked (set): Set of booked seat labels.
    Returns:
        list: List of available seat labels ordered by centrality.
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
    Args:
        seats (list): List of seat labels.
        seats_per_row (int): Number of seats in the row.
        take (int, optional): If provided, return only the most central N seats.
    Returns:
        list: List of seat labels ordered by centrality.
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

def default_seating(movie: Movie, num_tickets):
    """
    Assign the best available seats for a booking, ordered by centrality (most central first).
    Args:
        movie (Movie): The Movie instance to assign seats for.
        num_tickets (int): Number of tickets to assign.
    Returns:
        list: List of assigned seat labels (e.g., ['A5', 'A6']).
    """
    log_info(f"Assigning default seating for {num_tickets} tickets.")
    seat_map = build_seat_map(movie)
    booked = get_booked_seats(movie)
    ordered_seats = ordered_free_seat_map(seat_map, booked)
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

def custom_seating(movie: Movie, num_tickets, seat_input):
    """
    Assign custom seats for a booking, starting at a user-specified seat and filling according to the seating algorithm.
    Args:
        movie (Movie): The Movie instance to assign seats for.
        num_tickets (int): Number of tickets to assign.
        seat_input (str): The starting seat label (e.g., 'B4').
    Returns:
        list: List of assigned seat labels (e.g., ['B4', 'B5', ...]).
    """
    log_info(f"Assigning custom seating for {num_tickets} tickets starting at {seat_input}.")
    seat_map = build_seat_map(movie)
    booked = get_booked_seats(movie)
    assigned = []
    row = seat_input[0]
    start_num = int(seat_input[1:])
    seats_per_row = movie.seats_per_row
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


