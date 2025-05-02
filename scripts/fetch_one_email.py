import base64
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    # Get absolute paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    token_path = os.path.join(base_dir, 'credentials', 'token.json')
    secrets_path = os.path.join(base_dir, 'credentials', 'client_secrets.json')

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
        # Call the Gmail API users.messages.get
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().get(
            userId="me",
            # id="1968962246afbfa0",
            id="1968d47ebb69da27",
        ).execute()

        extracted_email = {}
        # id, labels, subject, body text

        if results:
            print("Message retrieved")
            # extract id
            message_id = results.get('id')
            extracted_email['id'] = message_id

            # extract labels
            labels = results.get('labelIds')
            for label in labels:
                if label.startswith("Label"):
                    extracted_email['label'] = label

            # extract subject
            payload = results.get("payload")
            headers_list = payload.get("headers")
            for entry in headers_list:
                if entry.get("name") == "Subject":
                    extracted_email["Subject"] = entry.get("value")

            # extract text
            get_data(extracted_email, payload)

            # save extracted email
            extracted_email['text'] = base64.urlsafe_b64decode(extracted_email['text']).decode('utf-8', errors='replace').replace('\r', '').replace('\n', '')
            with open(f'{extracted_email["id"]}.json', 'w') as f:
                json.dump(extracted_email, f, indent=4)

            # Save original email
            with open('email.json', 'w') as f:
                json.dump(results, f, indent=4)
        else:
            print("something went wrong")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def get_data(extracted_email, payload):
    if "parts" not in payload:
        if 'data' in payload.get("body"):
            if payload.get("body")["data"] and payload.get("mimeType") == "text/plain":
                extracted_email['text'] = payload.get("body")["data"] + " " + extracted_email.get('text', '')
    if payload.get('parts'):
        for part in payload.get('parts'):
            get_data(extracted_email, part)


if __name__ == "__main__":
    main()
