from src import logger, movie, booking
from src.validation import movie_validation, is_positive_integer, ticket_num_validation

def prompt_movie_creation():
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
            print("Checking bookings - feature not yet implemented.")
        elif choice == "3":
            logger.log_info("Exiting application.")
            print("Thank you for using GIC Cinemas system. Bye!")
            break
        else:
            logger.log_warning(f"Invalid menu selection: {choice}. Prompting again.")
            print("Invalid selection. Please try again.")

def booking_tickets_loop(movie_data):
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


def main():
    from src import logger
    logger.log_info("GIC CBS application started.")
    print("\nWelcome to the GIC CBS application!")
    movie_data = prompt_movie_creation()
    main_menu_loop(movie_data)
    print("Thank you for using GIC Cinemas system. Bye!")



if __name__ == "__main__":
    main()