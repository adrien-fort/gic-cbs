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
	Returns the modified Movie object.
	Accepts either a Movie instance..
	"""
	log_info(f"Attempting to unbook reservation for booking ID: {booking_id}")
	from src.movie_classes import Movie
	# Accept both Movie instance and dict for compatibility
	if isinstance(movie_json, Movie):
		movie_obj = movie_json
	else:
		log_error("movie_json is neither a Movie instance")
		return movie_json
	booking = movie_obj.get_booking(booking_id)
	if booking is not None:
		booking.status = 'R'
		log_info(f"Booking {booking_id} status set to 'R'.")
		from src.movie import save_movie
		save_movie(movie_obj)
	else:
		log_warning(f"Booking ID {booking_id} not found in movie bookings.")
	return movie_obj

def view_booking(movie_json, booking_id):
	"""
	For the given booking ID:
	1. Set status to 'R' (unbook_reservation)
	2. Display the movie seating (movie_display)
	3. Set status to 'B' (confirm_reservation)
	Returns the updated Movie object.
	Accepts only a Movie instance .
	"""
	log_info(f"Viewing booking for ID: {booking_id}")
	from src.movie_classes import Movie
	# Accept only Movie instance
	if isinstance(movie_json, Movie):
		movie_obj = movie_json
	else:
		log_error("movie_json is not a Movie instance.")
		return movie_json
	print(f"\nBooking ID: {booking_id}")
	movie_obj = unbook_reservation(movie_obj, booking_id)
	print(movie_display(movie_obj))
	movie_obj = confirm_reservation(movie_obj, booking_id)
	log_info(f"Booking {booking_id} reconfirmed after view.")
	return movie_obj