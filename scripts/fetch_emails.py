import base64
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.fetch_labeled_emails import extract

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

        # Call the Gmail API users.messages.list
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            maxResults=500,
            includeSpamTrash="false"
        ).execute()
        # if successful:
        # results = {
        #   "messages": [
        #     {
        #       object (Message)
        #     }
        #   ],
        #   "nextPageToken": string,
        #   "resultSizeEstimate": integer
        # }

        # where Message = {
        #   "id": string,
        #   "threadId": string
        # }
        #

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
                includeSpamTrash="false"
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                print("No messages found.")
                return

            for message in messages:
                ids.append(message["id"])

            next_page_token = results.get("nextPageToken", 0)

        # all ids retrieved at this point
        extracted_emails = {
            "emails": []
        }
        for i in range(min(100, len(ids))):
            try:
                # Call the Gmail API users.messages.get
                results = service.users().messages().get(
                    userId="me",
                    id=ids[i],
                ).execute()

                if results:
                    extracted_emails = extract(results, extracted_emails)
                    print("count: ", i)
                    # payload = results.get("payload")
                    # headers_list = payload.get("headers", [])
                    # extracted_email = {}
                    # if headers_list:
                    #     for entry in headers_list:
                    #         if entry.get("name") == "Subject":
                    #             extracted_email['subject'] = entry.get("value")
                    #             extracted_emails["emails"].append(extracted_email)

                else:
                    print("something went wrong")

            except HttpError as error:
                # TODO(developer) - Handle errors from gmail API.
                print(f"An error occurred: {error}")

        # for loop ends
        output_path = os.path.join('data', 'extracted_emails.json')
        with open(output_path, 'w') as outfile:
            json.dump(extracted_emails, outfile, indent=4)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
