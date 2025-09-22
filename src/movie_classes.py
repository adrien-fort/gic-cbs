
class Booking:
    """
    Represents a booking for a set of seats in a movie.
    Attributes:
        id (str): The booking ID (e.g., 'GIC0001').
        status (str): The booking status ('R' for reserved, 'B' for booked).
        seats (list): List of seat labels (e.g., ['A1', 'A2']).
    """
    def __init__(self, booking_id, status, seats):
        """
        Initialize a Booking instance.
        Args:
            booking_id (str): The booking ID.
            status (str): The booking status ('R' or 'B').
            seats (list): List of seat labels.
        """
        self.id = booking_id
        self.status = status
        self.seats = list(seats)

    @classmethod
    def from_dict(cls, data):
        """
        Create a Booking instance from a dictionary.
        Args:
            data (dict): Dictionary with keys 'ID', 'status', and 'seats'.
        Returns:
            Booking: The created Booking instance.
        """
        return cls(
            booking_id=data["ID"],
            status=data["status"],
            seats=data.get("seats", [])
        )

    def to_dict(self):
        """
        Convert the Booking instance to a dictionary.
        Returns:
            dict: Dictionary representation of the booking.
        """
        return {"ID": self.id, "status": self.status, "seats": self.seats}

    def __eq__(self, other):
        """
        Check equality with another Booking instance.
        Args:
            other (Booking): Another Booking instance.
        Returns:
            bool: True if equal, False otherwise.
        """
        return isinstance(other, Booking) and self.id == other.id and self.status == other.status and self.seats == other.seats


class Movie:
    """
    Represents a movie and its seating configuration and bookings.
    Attributes:
        title (str): The movie title.
        row (int): Number of rows in the theater.
        seats_per_row (int): Number of seats per row.
        bookings (list): List of Booking instances for this movie.
    """
    def __init__(self, title, row, seats_per_row, bookings=None):
        """
        Initialize a Movie instance.
        Args:
            title (str): The movie title.
            row (int): Number of rows.
            seats_per_row (int): Number of seats per row.
            bookings (list, optional): List of Booking instances.
        """
        self.title = title
        self.row = row
        self.seats_per_row = seats_per_row
        self.bookings = list(bookings) if bookings is not None else []

    @classmethod
    def from_dict(cls, data):
        """
        Create a Movie instance from a dictionary.
        Args:
            data (dict): Dictionary with keys 'title', 'row', 'seats_per_row', and 'bookings'.
        Returns:
            Movie: The created Movie instance.
        """
        bookings = [Booking.from_dict(b) for b in data.get("bookings", [])]
        return cls(
            title=data["title"],
            row=data["row"],
            seats_per_row=data["seats_per_row"],
            bookings=bookings
        )

    def to_dict(self):
        """
        Convert the Movie instance to a dictionary.
        Returns:
            dict: Dictionary representation of the movie.
        """
        return {
            "title": self.title,
            "row": self.row,
            "seats_per_row": self.seats_per_row,
            "bookings": [b.to_dict() for b in self.bookings]
        }

    def add_booking(self, booking):
        """
        Add a Booking instance to the movie's bookings list.
        Args:
            booking (Booking): The Booking instance to add.
        """
        self.bookings.append(booking)

    def get_booking(self, booking_id):
        """
        Retrieve a Booking instance by booking ID.
        Args:
            booking_id (str): The booking ID to search for.
        Returns:
            Booking or None: The Booking instance if found, else None.
        """
        for b in self.bookings:
            if b.id == booking_id:
                return b
        return None

    # There is no requirement for a specific booking removal strategy but this could be useful in the future
    def remove_booking(self, booking_id):
        """
        Remove a Booking instance from the bookings list by booking ID.
        Args:
            booking_id (str): The booking ID to remove.
        """
        self.bookings = [b for b in self.bookings if b.id != booking_id]
