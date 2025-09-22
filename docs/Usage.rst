
Usage
=====

The GIC Cinema Booking System is a command-line application for managing movie seat reservations, bookings, and seat availability.

To run the application:

1. Activate your Python virtual environment (if not already active):

	```
	source venv/bin/activate  # On Linux/macOS
	venv\Scripts\activate    # On Windows
	```

2. Start the booking system:

	```
	python -m src.main
	```


You will be guided through:

- Creating a movie and seating map
- Booking tickets (with best-available or custom seat selection)
- Checking bookings and seat status
- Viewing seat availability

All actions and errors are logged to the `logs/` directory for observability.
