# gic-cbs Project


## Overview
The `gic-cbs` project is a command-line cinema booking system for managing movie seat reservations, bookings, and seat availability. It is designed for demonstration, learning, and testing of robust booking logic, validation, and observability in Python. The project follows a Test-Driven Development (TDD) approach, ensuring all features are thoroughly tested before implementation.

## Installation
To install the necessary dependencies, you can use the following command:

```
pip install -r requirements.txt
```


## Usage
To run the cinema booking system, activate your virtual environment and execute:

```
python -m src.main
```


You will be prompted to create a movie, book tickets, check bookings, and view seat availability through a simple interactive menu. All actions and errors are logged for observability.

## Pipeline
The basic pipeline will run the tests, create a coverage artifact, run the sonarqube static scan (and use the artifact) and ultimately run Sphinx to create the versioned documentation with the doc artifact published.

## Running Tests
This project uses `pytest` for testing. To run the tests, execute the following command in your Python virtual env:

```
pytest
```

## Observability

As this is a very basic application which doesn't even have API, no advanced telemetry except for logging has been put in place. The code will automatically create a logs directory under the project root and one log file per day will be created. Logs will append to the same file on any given day if the app is restarted.

## Documentation
The documentation for the project is generated using Sphinx. You can build the documentation by navigating to the `docs` directory and running:

```
make html
```

The generated documentation will be available in the `_build/html` directory or as menntioned above the documentation is also auto-generated each time the CI pipeline runs.



## Contribution
Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch to your forked repository.
5. Create a pull request.

## License
This project is licensed under the MIT license. See the LICENSE file for more details.