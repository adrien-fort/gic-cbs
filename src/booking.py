import string
import copy

def book_ticket(movie_json, num_tickets):
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
    assigned_seats = default_seating(movie_json, num_tickets)
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
            continue
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

# Utility: Sort seats by centrality in a row, optionally taking only the most central N seats
def seat_sort_order(seats, seats_per_row, take=None):
    """
    Given a list of seat labels (e.g., ["A1", "A2", ...]), return them ordered by centrality.
    If take is provided, return only the most central N seats.
    """
    if not seats:
        return []
    # Determine row center
    center = get_row_center(seats_per_row)
    seat_nums = sorted([int(s[1:]) for s in seats])
    # Sort by centrality (distance to center), then by seat number ascending (rightmost first)
    seat_nums.sort(key=lambda n: (abs(n - center), -n))
    result = [f"{seats[0][0]}{n}" for n in seat_nums]
    if take:
        result = result[:take]
    return result

# Utility: Compute how close a block of seats is to the row center
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

def select_best_block(blocks, seats_per_row, group_size):
    """
    Given a list of contiguous seat blocks, select the best block for a group of given size.
    The best block is the one closest to the row center. Returns the most middle seats in the block.
    If no block is big enough, returns the largest available block (for partial assignment).
    Returns None if no blocks exist.
    """
    if not blocks:
        return None
    # Compute row center
    center = get_row_center(seats_per_row)
    big_enough = [b for b in blocks if len(b) >= group_size]
    if big_enough:
        # Sort blocks by the closest seat in the block to the row center
        def block_min_dist(b):
            seat_nums = [int(s[1:]) for s in b]
            return min(abs(n - center) for n in seat_nums)
        big_enough.sort(key=block_min_dist)
        block = big_enough[0]
        block_seats = seat_sort_order(block, seats_per_row, take=group_size)
        return block_seats
    # No block big enough, return the largest available block for partial assignment
    block = max(blocks, key=len)
    block_seats = seat_sort_order(block, seats_per_row)
    return block_seats


def default_seating(movie_json, num_tickets):
    """
    Assign the best available contiguous seats for the given group size.
    - Fills from row A (front) to last row.
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
    # 2. If not enough contiguous seats, assign the most central available blocks for the remaining seats
    if seats_needed > 0:
        assigned.extend(_assign_partial_blocks(rows, seat_map, booked, assigned, seats_per_row, seats_needed))
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
                # Score: sum of distances to center, then highest ending seat number (rightmost)
                score = (sum(abs(n - center) for n in subblock), -subblock[-1])
                candidates.append((score, [f"{block[0][0]}{n}" for n in sorted(subblock)]))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]

def _assign_partial_blocks(rows, seat_map, booked, assigned, seats_per_row, seats_needed):
    """
    Assign seats for remaining seats_needed by finding the most central available blocks in any row.
    Returns a list of seat labels assigned.
    """
    assigned_seats = []
    while seats_needed > 0:
        best_block = _find_best_partial_block(rows, seat_map, booked, assigned, assigned_seats, seats_per_row)
        if best_block is None:
            break  # No more available blocks
        row_letter, block_nums = best_block
        take = min(len(block_nums), seats_needed)
        # Build seat labels for the block
        block_seats = [f"{row_letter}{n}" for n in sorted(block_nums)]
        # Use seat_sort_order to pick the most central (and rightmost if tied) seats
        chosen_seats = seat_sort_order(block_seats, seats_per_row, take=take)
        assigned_seats.extend(chosen_seats)
        seats_needed -= take
    return assigned_seats

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

def _find_best_partial_block(rows, seat_map, booked, assigned, assigned_seats, seats_per_row):
    """
    Find the most central available block in any row, skipping already assigned seats.
    Returns (row_letter, block_nums) or None.
    """
    best_block = None
    best_block_score = None
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        available = [s for s in seat_map[row_letter] if s not in booked and s not in assigned and s not in assigned_seats]
        blocks = find_contiguous_blocks(available)
        for block in blocks:
            block_nums = [int(s[1:]) for s in block]
            if not block_nums:
                continue
            center = get_row_center(seats_per_row)
            block_center_val = sum(block_nums) / len(block_nums)
            # Score: row index (prefer lower/earlier rows), then centrality, then leftmost starting seat number, then longer block
            score = (i, abs(center - block_center_val), -max(block_nums), -len(block_nums))
            if best_block_score is None or score < best_block_score:
                best_block_score = score
                best_block = (row_letter, block_nums)
    return best_block