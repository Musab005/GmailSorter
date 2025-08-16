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

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    token_path = os.path.join(base_dir, 'credentials', 'token.json')
    secrets_path = os.path.join(base_dir, 'credentials', 'client_secrets.json')

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        old_WS = "Label_8393498597313348571"
        new_WS = "Label_6466171963081574403"

        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            maxResults=500,
            labelIds=[old_WS],
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
                maxResults=500,
                pageToken=next_page_token,
                labelIds=[old_WS],
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

        try:
            print("Total ids retrieved: ", len(ids))
            print("Changing labels ...")
            results = service.users().messages().batchModify(
                userId="me",
                body={
                    "ids": ids,
                    "addLabelIds": new_WS,
                    "removeLabelIds": [old_WS]
                }
            ).execute()
            # results = empty if successful

            if not results:
                print("Successfully changed labels")
            else:
                print("results: " + results)

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
