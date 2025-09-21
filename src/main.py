
"""
main.py
-------
Entry point and main user interface loop for the GIC Cinema Booking System.
Handles movie creation, main menu, and ticket booking flows.
"""

from src import logger, movie, booking, check_booking
from src.validation import movie_validation, is_positive_integer, ticket_num_validation, is_valid_booking

def prompt_movie_creation():
    """
    Prompt the user to define a movie title and seating map.
    Returns:
        dict: The created movie data.
    """
    logger.log_info("Prompting user for movie title and seating map.")
    while True:
        user_input = input("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ")
        is_valid = movie_validation(user_input)
        if is_valid:
            logger.log_info(f"Valid movie and seating map input received: {user_input}")
            movie_data = movie.create_movie(user_input)
            logger.log_info(f"Movie created: {movie_data}")
            movie.save_movie(movie_data)  # Save the newly created movie
            return movie_data
        else:
            logger.log_warning(f"Invalid input for movie and seating map: {user_input}. Prompting again.")
            print("Invalid input. Please try again.")

def main_menu_loop(movie_data):
    """
    Display the main menu and handle user selections for booking or checking bookings.
    Args:
        movie_data (dict): The current movie data.
    """
    while True:
        print("\nWelcome to GIC Cinemas")
        print("[1] Book tickets for "+ movie_data["title"] + " (" + str(movie.movie_available_seats(movie_data)) + " seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        choice = input("Please enter your selection:\n> ")
        if choice == "1":
            logger.log_info("User selected Booking tickets.")
            booking_tickets_loop(movie_data)
        elif choice == "2":
            logger.log_info("Checking bookings - feature not yet implemented.")
            check_booking_loop(movie_data)
        elif choice == "3":
            logger.log_info("Exiting application.")
            print("Thank you for using GIC Cinemas system. Bye!")
            break
        else:
            logger.log_warning(f"Invalid menu selection: {choice}. Prompting again.")
            print("Invalid selection. Please try again.")

def booking_tickets_loop(movie_data):
    """
    Prompt the user to enter the number of tickets to book and handle booking logic.
    Args:
        movie_data (dict): The current movie data.
    """
    while True:
        ticket_input = input("\nEnter number of tickets to book, or enter blank to go back to main menu:\n> ")
        logger.log_info(f"Booking prompt received input: '{ticket_input}'")
        if ticket_input.strip() == "":
            logger.log_info("User returned to main menu from booking prompt.")
            break
        elif not is_positive_integer(ticket_input):
            logger.log_warning(f"Invalid ticket input (not positive integer): '{ticket_input}'")
            print("Invalid input. Please enter a valid number of tickets or blank to go back.")
        else:
            available = movie.movie_available_seats(movie_data)
            logger.log_info(f"User requested {ticket_input} tickets; {available} seats available.")
            if int(ticket_input) > available:
                logger.log_warning(f"Requested tickets ({ticket_input}) exceed available seats ({available}).")
                if available == 1:
                    print("Sorry, there is only 1 seat available.")
                else:
                    print(f"Sorry, there are only {available} seats available.")
            elif ticket_num_validation(ticket_input, movie_data):
                logger.log_info(f"User requested to book {ticket_input} tickets. Validation passed.")
                movie_data = booking.book_ticket(movie_data, int(ticket_input))
                break
            else:
                logger.log_warning(f"Ticket input '{ticket_input}' failed ticket_num_validation.")
                print("Invalid input. Please enter a valid number of tickets or blank to go back.")

def check_booking_loop(movie_data):
    """
    Prompt the user to enter a booking ID in a loop to show the details of the booking selected.
    Args:
        movie_data (dict): The current movie data.
    """
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
    movie_data = prompt_movie_creation()
    main_menu_loop(movie_data)


if __name__ == "__main__":
    main()