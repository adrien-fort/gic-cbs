from src.logger import log_info, log_warning, log_error
from src.booking import get_booking_id, confirm_reservation, get_row_center, seat_sort_order, build_seat_map, get_booked_seats
import string

from src.movie_classes import Movie

# All functions below are hidden from users and are an attempt at a smarter seating algorithm
# The main driver being that a person is unlikely to want to sit in non-contiguous seats if they are booking multiple tickets

def book_ticket_advanced(movie: Movie, num_tickets):
    """
    Adds a booking to the movie's bookings array.
    Uses get_booking_id to generate the next booking ID.
    Returns the modified movie JSON.
    """
    from src.movie_classes import Booking
    from src.movie import save_movie, movie_display
    from src.validation import is_valid_seat

    log_info(f"[ADVANCED] Starting booking for {num_tickets} tickets for movie '{movie.title}'")
    booking_id = get_booking_id(movie)
    log_info(f"[ADVANCED] Generated booking ID: {booking_id}")
    booking = Booking(booking_id, "R", [])
    # Ensure bookings is a list
    if not hasattr(movie, "bookings") or not isinstance(movie.bookings, list):
        log_warning("[ADVANCED] 'bookings' attribute missing or not a list in movie. Initializing new list.")
        movie.bookings = []
    # Assign seats using default_seating_advanced (returns seat list)
    assigned_seats = default_seating_advanced(movie, num_tickets)
    booking.seats = assigned_seats
    log_info(f"[ADVANCED] Default seats assigned: {assigned_seats}")
    movie.bookings.append(booking)
    log_info(f"[ADVANCED] Booking object added to movie: {booking.__dict__}")
    print(f"\nSuccessfully reserved {num_tickets} {movie.title} tickets")
    while True:
        print(f"\nBooking ID: {booking_id}")
        print(movie_display(movie.to_dict()))
        seating_input = input("\nEnter blank to accept seat selection, or enter new seating position:\n> ")
        status = is_valid_seat(movie, seating_input)
        if status == "blank":
            log_info(f"[ADVANCED] Booking {booking_id} confirmed by user.")
            movie = confirm_reservation(movie, booking_id)
            log_info(f"[ADVANCED] Booking {booking_id} status set to 'B'.")
            save_movie(movie.to_dict())
            print(f"\nBooking ID: {booking_id} confirmed.\n")
            break
        elif status == "valid":
            assigned_seats = advanced_custom_seating(movie, num_tickets, seating_input.strip().upper())  # Placeholder, to be implemented
            log_info(f"[ADVANCED] Custom seating input '{seating_input.strip().upper()}' accepted. Seats assigned: {assigned_seats}")
            b = None
            if hasattr(movie, 'get_booking'):
                b = movie.get_booking(booking_id)
            if b:
                b.seats = assigned_seats
            save_movie(movie.to_dict())
            log_info(f"[ADVANCED] Booking {booking_id} updated with custom seats and saved.")
        else:
            log_warning(f"[ADVANCED] Invalid seat input '{seating_input.strip()}'; prompt user again.")
            print(f"Seat {seating_input.strip()} is not valid. Please try again or enter blank to accept.")
    return movie

def block_center(block, seats_per_row):
    log_info(f"[ADVANCED] Calculating block center for block: {block}")
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
    log_info(f"[ADVANCED] Finding contiguous blocks in available seats: {available}")
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
    log_info(f"[ADVANCED] Assigning advanced default seating for {num_tickets} tickets.")
    """
    Assign the best available contiguous seats for the given group size.
    - Fills from row A (back) to front row.
    - Picks the most middle seats available in a row.
    - Keeps groups together if possible; if not enough contiguous seats in a row, overflows to next row.
    - Skips already booked seats.
    Returns a list of assigned seat labels.
    """
    rows = movie_json.row
    seats_per_row = movie_json.seats_per_row
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
        return assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row)
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

def assign_single_seat_advanced(rows, seat_map, booked, assigned, seats_per_row):
    """
    Assign the most central/rightmost available seat for a single ticket booking.
    Returns a list with the assigned seat or empty if none available.
    """
    all_available = []
    for i in range(rows):
        row_letter = string.ascii_uppercase[i]
        for s in seat_map[row_letter]:
            if s not in booked and s not in assigned:
                all_available.append(s)
    if not all_available:
        return []
    sorted_seats = seat_sort_order(all_available, seats_per_row, take=1)
    if sorted_seats:
        return [sorted_seats[0]]
    return []

def assign_from_starting_seat(seat_map, booked, row, start_num, num_tickets):
    """Assign as many contiguous seats as possible in the starting row from the input seat."""
    available_in_row = [s for s in seat_map[row] if s not in booked]
    blocks = find_contiguous_blocks(available_in_row)
    block_with_input = None
    for block in blocks:
        if f"{row}{start_num}" in block:
            block_with_input = block
            break
    if block_with_input:
        seat_nums = [int(s[1:]) for s in block_with_input]
        seat_nums.sort()
        idx = seat_nums.index(start_num)
        seats_order = [start_num]
        r, l = 1, 0
        while len(seats_order) < len(seat_nums):
            if idx + r < len(seat_nums):
                seats_order.append(seat_nums[idx + r])
                r += 1
            if idx - l - 1 >= 0:
                seats_order.append(seat_nums[idx - l - 1])
                l += 1
        seats_order = seats_order[:min(num_tickets, len(seat_nums))]
        return [f"{row}{n}" for n in sorted(seats_order)]
    else:
        return [f"{row}{start_num}"]

def find_best_subblock(blocks, seats_needed, seats_per_row):
    """Find the most central sub-block of the required size among all blocks."""
    best_subblock = None
    best_score = None
    for block in blocks:
        if len(block) >= seats_needed:
            nums = [int(s[1:]) for s in block]
            for i in range(len(nums) - seats_needed + 1):
                sub_nums = nums[i:i+seats_needed]
                subblock = [f"{block[0][0]}{n}" for n in sub_nums]
                center = (seats_per_row + 1) / 2
                block_center = sum(sub_nums) / len(sub_nums)
                score = (abs(block_center - center), -max(sub_nums))
                if best_score is None or score < best_score:
                    best_score = score
                    best_subblock = subblock
    return best_subblock

def assign_overflow_rows(seat_map, booked, assigned, row_letters, row_idx, seats_needed, seats_per_row):
    """Assign seats in overflow rows, prioritizing largest/most central contiguous blocks."""
    for next_row_idx in range(row_idx + 1, len(row_letters)):
        if seats_needed <= 0:
            break
        next_row = row_letters[next_row_idx]
        available_in_next_row = [s for s in seat_map[next_row] if s not in booked and s not in assigned]
        if not available_in_next_row:
            continue
        blocks = find_contiguous_blocks(available_in_next_row)
        best_subblock = find_best_subblock(blocks, seats_needed, seats_per_row)
        if best_subblock:
            assigned.extend(best_subblock)
            seats_needed = 0
        else:
            # If no block is big enough, take the largest (most central) block, then continue
            if blocks:
                def block_score(block):
                    nums = [int(s[1:]) for s in block]
                    center = (seats_per_row + 1) / 2
                    block_center = sum(nums) / len(nums)
                    return (-len(block), abs(block_center - center), -max(nums))
                best_block = min(blocks, key=block_score)
                take = min(seats_needed, len(best_block))
                assigned.extend(best_block[:take])
                seats_needed -= take
    return assigned, seats_needed

def assign_fallback_seats(seat_map, booked, assigned, row_letters, seats_needed):
    """Assign any available seats (non-contiguous fallback)."""
    all_available = []
    for r in row_letters:
        for s in seat_map[r]:
            if s not in booked and s not in assigned:
                all_available.append(s)
    assigned.extend(all_available[:seats_needed])
    return assigned

def advanced_custom_seating(movie, num_tickets, seat_input):
    """
    Assign seats for advanced custom seating:
    - Start from the user-input seat.
    - Prioritize contiguous block in the same row (rightmost in tie).
    - If not enough, overflow to next row, maintaining contiguity.
    - Centrality is secondary to contiguity.
    Returns a list of assigned seat labels.
    """
    import string
    seat_map = build_seat_map(movie)
    booked = get_booked_seats(movie)
    row = seat_input[0]
    start_num = int(seat_input[1:])
    seats_per_row = movie.seats_per_row
    row_letters = list(seat_map.keys())
    row_idx = row_letters.index(row)

    # 1. Assign as much as possible contiguously in the same row, starting at the input seat
    assigned = assign_from_starting_seat(seat_map, booked, row, start_num, num_tickets)
    seats_needed = num_tickets - len(assigned)

    # 2. Try to fill next rows, prioritizing largest contiguous block (then centrality of block)
    if seats_needed > 0:
        assigned, seats_needed = assign_overflow_rows(seat_map, booked, assigned, row_letters, row_idx, seats_needed, seats_per_row)

    # 3. Fallback: if still not enough, fill with any available seat (non-contiguous)
    if seats_needed > 0:
        assigned = assign_fallback_seats(seat_map, booked, assigned, row_letters, seats_needed)
    return assigned