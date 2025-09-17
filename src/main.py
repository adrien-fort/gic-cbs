from src import logger
from src.validation import movie_validation
from src import movie

def main():
    logger.log_info("GIC CBS application started.")
    print("\nWelcome to the GIC CBS application!")
    logger.log_info("Prompting user for movie title and seating map.")
    while True:
        user_input = input("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n")
        is_valid = movie_validation(user_input)
        if is_valid:
            logger.log_info(f"Valid movie and seating map input received: {user_input}")
            movie_data = movie.create_movie(user_input)
            logger.log_info(f"Movie created: {movie_data}")
            break
        else:
            logger.log_warning(f"Invalid input for movie and seating map: {user_input}. Prompting again.")
            print("Invalid input. Please try again.")
    
    while True:
        print("\nWelcome to GIC Cinemas")
        print("[1] Book tickets for "+ movie_data["title"] + " (" + str(movie.movie_available_seats(movie_data)) + " seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        choice = input("Please enter your selection:")
        if choice == "1":
            logger.log_info("Booking tickets - feature not yet implemented.")
            print("Booking tickets - feature not yet implemented.")
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

if __name__ == "__main__":
    main()