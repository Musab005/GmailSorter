import os.path
#TODO: instead of checking for "not labels" check if no custom labels applied and no INBOX label
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cognitive_inbox.src.label_verifier import is_unlabelled

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    # Get absolute paths
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    data_dir = os.path.join(root_dir, "data")
    token_path = os.path.join(root_dir, 'credentials', 'token.json')
    secrets_path = os.path.join(root_dir, 'credentials', 'client_secrets.json')

    creds = None

    # Load credentials if token file exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If credentials are missing or invalid
    if not creds or not creds.valid:
        print("creds missing or invalid")
        if creds and creds.expired and creds.refresh_token:
            print("requesting refresh token")
            creds.refresh(Request())
        else:
            print("starting new auth flow")
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

        unlabelled_ids = []

        for i in range(len(ids)):
            try:
                # Call the Gmail API users.messages.get
                results = service.users().messages().get(
                    userId="me",
                    id=ids[i],
                ).execute()

                if results:
                    if is_unlabelled(results):
                        unlabelled_ids.append(results.get("id"))
                else:
                    print("something went wrong")

            except HttpError as error:
                # TODO(developer) - Handle errors from gmail API.
                print(f"An error occurred: {error}")

        # for loop ends here
        with open(f"{data_dir}/unlabelled_ids.txt", "w") as f:
            for idnum in unlabelled_ids:
                f.write(idnum + "\n")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
