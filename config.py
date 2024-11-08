"""
path: config.py
This file contains the settings for the project.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME","Data Sync")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION","0.1.0")
    HOUSECALL_API_KEY: str = os.getenv("HOUSECALL_API_KEY", "test")

    # Zoho
    ZOHO_CLIENT_ID: str = os.getenv("ZOHO_CLIENT_ID", "test")
    ZOHO_CLIENT_SECRET: str = os.getenv("ZOHO_CLIENT_SECRET", "test")
    ZOHO_AUTH_CODE: str = os.getenv("ZOHO_AUTH_CODE", "test")
    ZOHO_REDIRECT_URI: str = os.getenv("ZOHO_REDIRECT_URI", "test")

    # Google Sheets
    CREDENTIALS_FILE_PATH: str = os.getenv("CREDENTIALS_FILE_PATH", "credentials.json")
    SPREADSHEET_NAME: str = os.getenv("SPREADSHEET_NAME", "Data Sync")
    SHEET_NAME: str = os.getenv("SHEET_NAME", "Zoho Deals")
    SHEET_NAME2: str = os.getenv("SHEET_NAME2", "Zoho Accounts")


settings = Settings()
