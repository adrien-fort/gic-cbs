"""
check_booking.py
----------------
This module will provide functions to check and display bookings for a given movie.
"""
from src.logger import log_info, log_warning, log_error
from src.movie import movie_display
from src.booking import confirm_reservation

def unbook_reservation(movie_json, booking_id):
	"""
	Set the status of the booking with the given ID to 'R' (reserved).
	Returns the modified movie_json.
	"""
	log_info(f"Attempting to unbook reservation for booking ID: {booking_id}")
	found = False
	for booking in movie_json.get("bookings", []):
		if booking.get("ID") == booking_id:
			booking["status"] = "R"
			found = True
			log_info(f"Booking {booking_id} status set to 'R'.")
	if not found:
		log_warning(f"Booking ID {booking_id} not found in movie bookings.")
	return movie_json

def view_booking(movie_json, booking_id):
	"""
	For the given booking ID:
	1. Set status to 'R' (unbook_reservation)
	2. Display the movie seating (movie_display)
	3. Set status to 'B' (confirm_reservation)
	Returns the updated movie_json.
	"""
    
	log_info(f"Viewing booking for ID: {booking_id}")
	print(f"\nBooking ID: {booking_id}")
	movie_json = unbook_reservation(movie_json, booking_id)
	print(movie_display(movie_json))
	movie_json = confirm_reservation(movie_json, booking_id)
	log_info(f"Booking {booking_id} reconfirmed after view.")
	return movie_json