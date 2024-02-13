<!-- Make sure you have Python and `virtualenv` installed. -->

# Install virtualenv using pip
pip install virtualenv

<!-- Setting Up Virtual Environment -->
# Open a terminal or command prompt.
# Navigate to the project's root directory.

# On Windows
python -m venv data_scrap

# On macOS/Linux
python3 -m venv data_scrap

<!-- Activating Virtual Environment -->

# On Windows
.\data_scrap\Scripts\activate

# On macOS/Linux
source data_scrap/bin/activate

# Install project dependencies:
pip install -r requirements.txt

# Execute the project by running the main script 
python main.py

