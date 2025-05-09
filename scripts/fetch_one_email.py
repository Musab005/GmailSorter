import base64
import json
import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.email_extractor import extract_message

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    # Get absolute paths
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    sample_file = os.path.join(root_dir, "data/sample-email.json")
    extracted_file = os.path.join(root_dir, "data")
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

    data = {
        "id": [],
        "label": [],
        "subject": [],
        "text": []
    }

    try:
        # Call the Gmail API users.messages.get
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().get(
            userId="me",
            id="196a18e9e99b88fc",
        ).execute()

        if results:
            print("Message retrieved")
            extract_message(results, data)
            # Write extracted email to CSV
            df = pd.DataFrame(data)
            df.to_csv(f"{extracted_file}/email-{data['id'][0]}.csv", index=False, encoding="utf-8")

            # Save original email as sample.json
            with open(sample_file, 'w', encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=True, indent=4)
        else:
            print("something went wrong")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
