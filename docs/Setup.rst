
Setup
=====

To set up the GIC Cinema Booking System locally:

1. **Clone the repository:**

	```
	git clone https://github.com/adrien-fort/gic-cbs.git
	cd gic-cbs
	```

2. **Create and activate a Python virtual environment:**

	On Linux/macOS:
	```
	python3 -m venv venv
	source venv/bin/activate
	```
	On Windows:
	```
	python -m venv venv
	venv\Scripts\activate
	```

3. **Install dependencies:**

	```
	pip install -r requirements.txt
	```

4. **(Optional) Run tests to verify setup:**

	```
	pytest
	```

5. **(Optional) Build documentation:**

	```
	cd docs
	make html  # or: python -m sphinx -b html . _build/html
	```

You are now ready to use the GIC Cinema Booking System!
