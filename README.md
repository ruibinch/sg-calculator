# Overview

Backend RESTful API running on Python Flask.

## Setting up

1. Clone the repository

2. Create and activate a Python virtual environment (either via `conda` or `virtualenv`)
```bash
virtualenv venv
. venv/bin/activate
```

3. Install the dependencies
```
$ pip install -r requirements.txt
```

4. Run the development server
```
$ python app.py
```

The app will run on [http://localhost:5000](http://localhost:5000).

## Running unit tests

Testing framework used is `pytest`. <br>
Tests are located in */tests* folder.

To run the unit tests,
```
$ pytest
```