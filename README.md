# Social Simulate

## Setup

1. Ensure you have Python 3.12.0 installed
2. Clone this repository
3. Run the setup script:
   - On Unix-based systems: `./setup.sh`
   - On Windows: `setup.bat`
4. Activate the virtual environment:
   - On Unix-based systems: `source fastapi-env/bin/activate`
   - On Windows: `fastapi-env\Scripts\activate`
5. Create a `.env` file in the project root directory with the following content:

    ```text
    DATABASE_URL=your_database_url_here
    SECRET_KEY=your_secret_key_here
    ```

    Replace `your_database_url_here` and `your_secret_key_here` with your actual database URL and a secure secret key.
