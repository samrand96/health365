"""
Loads environment variables from a .env file using dotenv and assigns them to corresponding constants.

Constants:
    - DB_URL (str): The URL for the database connection.
    - SECRET_KEY (str): The secret key used for cryptographic operations.
    - ALGORITHM (str): The algorithm used for cryptographic operations.
    - ACCESS_TOKEN_EXPIRE (str): The expiration time for access tokens in minutes.
    - SENDGRID_API_KEY (str): The API key for SendGrid service.
    - FROM_EMAIL (str): The email address used as the sender in email communication.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL')