
"""
main.py
-------
Entry point and main user interface loop for the GIC Cinema Booking System.
Handles movie creation, main menu, and ticket booking flows.
"""

from src import booking_advanced, logger, movie, booking, check_booking
from src.movie_classes import Movie

from src.validation import movie_validation, is_positive_integer, ticket_num_validation, is_valid_booking


# Constant for repeated invalid input message
INVALID_TICKET_INPUT_MSG = "Invalid input. Please enter a valid number of tickets or blank to go back."

def prompt_movie_creation():
    """
    Prompt the user to define a movie title and seating map.
    Returns:
        Movie: The created Movie instance.
    """
    logger.log_info("Prompting user for movie title and seating map.")
    while True:
        user_input = input("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ")
        is_valid = movie_validation(user_input)
        if is_valid:
            logger.log_info(f"Valid movie and seating map input received: {user_input}")
            movie_obj = movie.create_movie(user_input)
            logger.log_info(f"Movie created: {movie_obj}")
            movie.save_movie(movie_obj)  # Save the newly created movie
            return movie_obj
        else:
            logger.log_warning(f"Invalid input for movie and seating map: {user_input}. Prompting again.")
            print("Invalid input. Please try again.")

def main_menu_loop(movie_data):
    """
    Display the main menu and handle user selections for booking or checking bookings.
    Args:
        movie_data (Movie): The current Movie instance.
    """
    while True:
        print("\nWelcome to GIC Cinemas")
        print(f"[1] Book tickets for {movie_data.title} (" + str(movie.movie_available_seats(movie_data)) + " seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        choice = input("Please enter your selection:\n> ")
        if choice == "1":
            logger.log_info("User selected Booking tickets.")
            booking_tickets_loop(movie_data, mode="standard")
        elif choice == "2":
            logger.log_info("Checking bookings - feature not yet implemented.")
            check_booking_loop(movie_data)
        elif choice == "3":
            logger.log_info("Exiting application.")
            print("\nThank you for using GIC Cinemas system. Bye!")
            break
        elif choice == "9":  # Hidden advanced booking option
            logger.log_info("User selected hidden Booking Advanced tickets option.")
            booking_tickets_loop(movie_data, mode="advanced")
        else:
            logger.log_warning(f"Invalid menu selection: {choice}. Prompting again.")
            print("Invalid selection. Please try again.")

def booking_tickets_loop(movie_data, mode):
    """
    Prompt the user to enter the number of tickets to book and handle booking logic.
    Args:
        movie_data (Movie): The current Movie instance.
    """
    from src import booking
    while True:
        ticket_input = input("\nEnter number of tickets to book, or enter blank to go back to main menu:\n> ")
        logger.log_info(f"Booking prompt received input: '{ticket_input}'")
        if ticket_input.strip() == "":
            logger.log_info("User returned to main menu from booking prompt.")
            break
        elif not is_positive_integer(ticket_input):
            logger.log_warning(f"Invalid ticket input (not positive integer): '{ticket_input}'")
            print(INVALID_TICKET_INPUT_MSG)
        else:
            available = movie.movie_available_seats(movie_data)
            logger.log_info(f"User requested {ticket_input} tickets; {available} seats available.")
            if int(ticket_input) > available:
                logger.log_warning(f"Requested tickets ({ticket_input}) exceed available seats ({available}).")
                print_seat_availability_warning(available)
            elif ticket_num_validation(ticket_input, movie_data):
                logger.log_info(f"User requested to book {ticket_input} tickets. Validation passed.")
                if mode == "standard":
                    movie_data = booking.book_ticket(movie_data, int(ticket_input))
                elif mode == "advanced":
                    movie_data = booking_advanced.book_ticket_advanced(movie_data, int(ticket_input))
                break
            else:
                logger.log_warning(f"Ticket input '{ticket_input}' failed ticket_num_validation.")
                print(INVALID_TICKET_INPUT_MSG)

def print_seat_availability_warning(available):
    """
    Print a warning message about limited seat availability.
    Args:
        available (int): The number of available seats.
    """
    if available == 1:
        print("Sorry, there is only 1 seat available.")
    elif available == 0:
        print("Sorry, there are no seats available.")
    else:
        print(f"Sorry, there are only {available} seats available.")

def check_booking_loop(movie_data):
    """
    Prompt the user to enter a booking ID in a loop to show the details of the booking selected.
    Args:
        movie_data (Movie): The current Movie instance.
    """
    # Check if there are any bookings in the movie
    if not movie_data.bookings:
        print("There are currently no bookings.")
        logger.log_info("No bookings found in movie. Returning to main menu.")
        return
    while True:
        booking_id = input("\nEnter booking ID, or enter blank to go back to main menu:\n> ")
        if booking_id.strip() == "":
            logger.log_info("User exited check booking loop to return to main menu.")
            print("Returning to main menu.")
            break
        logger.log_info(f"User entered booking ID: {booking_id.strip()}")
        if is_valid_booking(movie_data, booking_id.strip()):
            logger.log_info(f"Booking ID '{booking_id.strip()}' is valid.")
            movie_data = check_booking.view_booking(movie_data, booking_id.strip())
        else:
            logger.log_warning(f"Booking ID '{booking_id.strip()}' is invalid.")
            print(f"Booking ID '{booking_id.strip()}' not found. Please try again.")

def main():
    """
    Main entry point for the GIC Cinema Booking System application.
    Initializes the app, prompts for movie creation, and starts the main menu loop.
    """
    from src import logger
    logger.log_info("GIC CBS application started.")
    print("\nWelcome to the GIC CBS application!")
    movie_obj = prompt_movie_creation()
    main_menu_loop(movie_obj)


if __name__ == "__main__":
    main()