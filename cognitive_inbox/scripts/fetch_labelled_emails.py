import os.path
import time

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cognitive_inbox.src.email_extractor import extract_message
from cognitive_inbox.src.label_verifier import is_labelled

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

        # Call the Gmail API users.messages.list
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            maxResults=500,
            includeSpamTrash=False
        ).execute()

        # list of message objects
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        ids = []
        for message in messages:
            ids.append(message["id"])

        next_page_token = results.get("nextPageToken", 0)
        while next_page_token:
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(
                userId="me",
                maxResults=500,
                pageToken=next_page_token,
                includeSpamTrash=False
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                print("No messages found.")
                return

            for message in messages:
                ids.append(message["id"])

            next_page_token = results.get("nextPageToken", 0)

        # all ids retrieved at this point
        print("number of emails retrieved: ", len(ids))

        data = {
            "id": [],
            "label": [],
            "subject": [],
            "text": []
        }
        start_time = time.time()
        count = 0
        for i in range(len(ids)):
            try:
                # Call the Gmail API users.messages.get
                results = service.users().messages().get(
                    userId="me",
                    id=ids[i],
                ).execute()

                if results:
                    if is_labelled(results):
                        extract_message(results, data)
                        count += 1
                        if count % 500 == 0:
                            print("count: ", count)
                else:
                    print("something went wrong")

            except HttpError as error:
                # TODO(developer) - Handle errors from gmail API.
                print(f"An error occurred: {error}")

        # for loop ends
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds")
        print(len(data['id']))
        print(len(data['subject']))
        print(len(data['label']))
        print(len(data['text']))
        df = pd.DataFrame(data)
        df.to_csv(extracted_emails_path, index=False, encoding="utf-8")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
