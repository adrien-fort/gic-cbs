from src.booking import get_booking_id, confirm_reservation, get_row_center, seat_sort_order, build_seat_map, get_booked_seats
import string

# All functions below are hidden from users and are an attempt at a smarter seating algorithm
# The main driver being that a person is unlikely to want to sit in non-contiguous seats if they are booking multiple tickets

def book_ticket_advanced(movie_json, num_tickets):
    """
    Adds a booking to the movie's bookings array.
    Uses get_booking_id to generate the next booking ID.
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
    assigned_seats = default_seating_advanced(movie_json, num_tickets)
    booking["seats"] = assigned_seats
    
    movie_json["bookings"].append(booking)
    while True:
        print(f"\nBooking ID: {booking_id}")
        # here we will call the display function
        seating_input = input("\nEnter blank to accept seat selection, or enter new seating position:\n")
        if seating_input.strip() == "":
            movie_json = confirm_reservation(movie_json, booking_id)
            break
        else:
            print("Seat selection modification not yet implemented. Please enter blank to accept.")
    return movie_json

def block_center(block, seats_per_row):
    """
    Given a block of seat labels (e.g., ["A4", "A5", "A6"]) and seats_per_row, return the absolute distance
    from the block's center to the row center (lower is more central).
    """
    if not block:
        return float('inf')
    center = get_row_center(seats_per_row)
    nums = [int(s[1:]) for s in block]
    return abs(center - (sum(nums) / len(nums)))

def find_contiguous_blocks(available):
    """
    Given a list of available seat labels in a row, return a list of all contiguous seat blocks.
    Each block is a list of seat labels.
    """
    blocks = []
    block = []
    for seat in available:
        if not block or int(seat[1:]) == int(block[-1][1:]) + 1:
            block.append(seat)
        else:
            if block:
                blocks.append(block)
            block = [seat]
    if block:
        blocks.append(block)
    return blocks

def default_seating_advanced(movie_json, num_tickets):
    """
    Assign the best available contiguous seats for the given group size.
    - Fills from row A (back) to front row.
    - Picks the most middle seats available in a row.
    - Keeps groups together if possible; if not enough contiguous seats in a row, overflows to next row.
    - Skips already booked seats.
    Returns a list of assigned seat labels.
    """
    rows = movie_json["row"]
    seats_per_row = movie_json["seats_per_row"]
    seat_map = build_seat_map(movie_json)
    booked = get_booked_seats(movie_json)
    seats_needed = num_tickets
    assigned = []
    # 1. Try to assign all seats in one contiguous block in any row (front to back)
    best_block = _find_first_row_with_block(rows, seat_map, booked, assigned, seats_per_row, seats_needed)
    if best_block:
        assigned.extend(best_block)
        seats_needed -= len(best_block)
        return assigned  # Always prefer a single contiguous block if possible
    # 2. If not enough contiguous seats, assign seats row by row (front to back), picking most central/rightmost in each row
    if num_tickets == 1:
        # For a single seat, always pick the most central/rightmost seat using seat_sort_order
        all_available = []
        for i in range(rows):
            row_letter = string.ascii_uppercase[i]
            for s in seat_map[row_letter]:
                if s not in booked and s not in assigned:
                    all_available.append(s)
        if not all_available:
            return assigned
        sorted_seats = seat_sort_order(all_available, seats_per_row, take=1)
        if sorted_seats:
            assigned.append(sorted_seats[0])
        return assigned
    for i in range(rows):
        if seats_needed <= 0:
            break
        row_letter = string.ascii_uppercase[i]
        row_available = [s for s in seat_map[row_letter] if s not in booked and s not in assigned]
        if not row_available:
            continue
        pick = min(seats_needed, len(row_available))
        assigned_in_row = seat_sort_order(row_available, seats_per_row, take=pick)
        assigned.extend(assigned_in_row)
        seats_needed -= len(assigned_in_row)
    return assigned

def _find_best_block_in_row(available, seats_per_row, seats_needed):
    """
    Given available seats in a row, return the best contiguous block of size seats_needed, or None.
    Returns a list of seat labels if found, else None.
    """
    blocks = find_contiguous_blocks(available)
    if not blocks:
        return None
    center = get_row_center(seats_per_row)
    candidates = []
    for block in blocks:
        if len(block) >= seats_needed:
            seat_nums = [int(s[1:]) for s in block]
            seat_nums.sort()
            for i in range(len(seat_nums) - seats_needed + 1):
                subblock = seat_nums[i:i+seats_needed]
                # Centrality: sum of distances to center
                centrality = sum(abs(n - center) for n in subblock)
                # For tiebreakers: prefer rightmost block (highest starting seat number)
                rightmost = max(subblock)
                start_seat = subblock[0]
                # Lower centrality is better, then higher rightmost, then higher start_seat
                score = (centrality, -rightmost, -start_seat)
                candidates.append((score, [f"{block[0][0]}{n}" for n in subblock]))
    if not candidates:
        return None
    # Sort by centrality, then by rightmost seat, then by rightmost starting seat
    candidates.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]))
    # Pick the first candidate (most central, rightmost in tie)
    return candidates[0][1]

def _find_first_row_with_block(rows, seat_map, booked, assigned, seats_per_row, seats_needed):
    """
    Find the first row (front to back) with a contiguous block of seats_needed available seats.
    Returns the list of seat labels if found, else None.
    """
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        available = [s for s in seat_map[row_letter] if s not in booked and s not in assigned]
        best_block = _find_best_block_in_row(available, seats_per_row, seats_needed)
        if best_block:
            return best_block
    return None

