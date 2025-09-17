from src import logger
from src.validation import movie_validation

def main():
    logger.log_info("GIC CBS application started.")
    print("Welcome to the GIC CBS application!")
    logger.log_info("Prompting user for movie title and seating map.")
    while True:
        user_input = input("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n")
        is_valid = movie_validation(user_input)
        if is_valid:
            logger.log_info(f"Valid movie and seating map input received: {user_input}")
            break
        else:
            logger.log_warning(f"Invalid input for movie and seating map: {user_input}. Prompting again.")
            print("Invalid input. Please try again.")
    print("Welcome to GIC Cinemas")

if __name__ == "__main__":
    main()