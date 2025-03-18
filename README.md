# Scraper-ChatGPT-with-Python-Flask
Scraper ChatGPT with Python Flask is a web app that scrapes data from ChatGPT, stores it in a MySQL database, and preprocesses the data. Users can view both raw and processed data. Built with Python (Flask), MySQL, and Selenium, it includes user authentication with login and registration features.

### Key Components:
- **app.py**: Contains the backend logic for handling scraping, user sessions, and database management.
- **Database (implementasi.sql)**: SQL file for setting up the required MySQL database structure.
- **HTML Templates**: Includes various pages like home, login, registration, and result viewing.


### Installation Steps:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/MHisyamAvilaS17/Scraper-ChatGPT-with-Flask.git

2. **Install the required dependencies:**
   pip install -r requirements.txt

3. **Set up MySQL Database:**

  - Run the SQL script implementasi.sql to set up the database.
  - Update the database connection details in app.py.

4. **Create** .env **file:**

    Add a .env file to store the SECRET_KEY for session management:
   SECRET_KEY=your_secret_key

5. **Run the Flask app:**
   flask run
The app will be running at http://127.0.0.1:5000/.

### Usage

  1.  Register a new account on the platform.
  2.  Log in with your registered credentials.
  3.  Start a new scraping session on the home page by entering the URL for ChatGPT scraping.
  4.  Preprocess the scraped data by choosing either Lower Case or Upper Case conversion.
  5.  Review your past scraping sessions or delete unwanted data.
