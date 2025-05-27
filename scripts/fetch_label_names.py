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
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

    names = []

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        if not labels:
            print("No labels found.")
            return
        for label in labels:
            names.append(label["name"])


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    with open(f"{base_dir}/data/names.txt", "w") as f:
        for name in names:
            f.write(name + "\n")


if __name__ == "__main__":
    main()
