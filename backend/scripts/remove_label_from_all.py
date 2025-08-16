import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cognitive_inbox.src.global_store import get_category_labels

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

        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            includeSpamTrash="false"
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
                pageToken=next_page_token,
                includeSpamTrash="false"
            ).execute()

            # list of message objects
            messages = results.get("messages", [])

            if not messages:
                print("No messages found.")
                return

            for message in messages:
                ids.append(message["id"])

            next_page_token = results.get("nextPageToken", 0)

        print("Total ids retrieved: ", len(ids))

        for i in range(0, len(ids), 1000):
            curr_ids = ids[i:i + 1000]
            print("Running batch: ", i)
            try:
                results = service.users().messages().batchModify(
                    userId="me",
                    body={
                        "ids": curr_ids,
                        "removeLabelIds": get_category_labels()
                    }
                ).execute()
                # results = empty if successful

                if not results:
                    print("Successfully changed labels")
                else:
                    print("error: " + results)

            except HttpError as error:
                # TODO(developer) - Handle errors from gmail API.
                print(f"An error occurred: {error}")




    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
