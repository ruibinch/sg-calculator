# Overview

Backend RESTful API running on Python Flask.

## Setting up

1. Clone the repository

2. Create and activate a Python virtual environment (either via `conda` or `virtualenv`)
```bash
# For python 2.7
sudo apt install python-pip
# For python 3
sudo apt install python3-pip
pip3 install virtualenv
python3 -m virtualenv -p python3 venv
source venv/bin/activate
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```

4. Run the development server
```bash
python app.py
```

The app will run on [http://localhost:5000](http://localhost:5000).

## Running unit tests

Testing framework used is `pytest`. <br>
Tests are located in */tests* folder.

To run the unit tests,
```bash
pytest
```