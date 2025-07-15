import os.path
import time
import requests

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.email_extractor import extract_message
from src.label_verifier import is_labelled

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    # Get absolute paths
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    extracted_emails_path = os.path.join(root_dir, "data/extracted_emails.csv")
    token_path = os.path.join(root_dir, 'credentials', 'token.json')
    secrets_path = os.path.join(root_dir, 'credentials', 'client_secrets.json')

    creds = None

    # Load credentials if token file exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If credentials are missing or invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the new token
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    try:

        url = "https://storage.googleapis.com/storage/v1/b/gmail-sorter-project/o"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        print(response.text)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
