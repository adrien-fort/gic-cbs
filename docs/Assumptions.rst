Assumptions
===========

The code is currently designed around several assumptions:
    | 1)The movie name can be more than one word and even have a number (e.g. Die Hard 2)
    | 2)0 is not an acceptable number for # of rows or # of seats per row, this would not make sense in the real world
    | 3)While the current code wouldn't allow for a booking ID to be skipped the code is currently build to create a new ID which is +1 from the max existing ID 

Snippet
--------

1) This is handled in the validation and movie module by taking the user_input string and splitting it into parts, the last two parts are converted to integers for row and seats_per_row, the rest is joined back together for the title

.. code-block:: python

        parts = user_input.strip().split()
        title = " ".join(parts[:-2])
        row = int(parts[-2])
        seats_per_row = int(parts[-1])

2) This is simply handled in the validation module by checking if the integers for row and seats_per_row are between 1 and their respective maximums (26 for rows, 50 for seats_per_row)

.. code-block:: python

        row_int = int(row)
        seats_int = int(seats_per_row)
        if not (1 <= row_int <= 26):
            return False
        if not (1 <= seats_int <= 50):
            return False
        return True

2) This is simply handled the booking module via the below simple look up loop:

.. code-block:: python

    for booking in bookings:
            bid = booking.get("ID", "")
            if bid.startswith("GIC") and bid[3:].isdigit():
                num = int(bid[3:])
                if num > max_id:
                    max_id = num
        next_id = max_id + 1
