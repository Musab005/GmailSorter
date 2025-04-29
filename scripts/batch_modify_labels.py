import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels", "https://www.googleapis.com/auth/gmail.modify"]


def main():
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        query_email = "from:FidoBill@fidomobile.ca"
        al_meezan_id = "Label_1171309637714112730"
        meezan_id = "Label_7249719907569470582"
        scotiabank_id = "Label_8900035065918535414"
        wealthsimple_id = "Label_8393498597313348571"
        reciepts_id = "Label_5039532840471697976"
        phone_id = "Label_8973070974094460398"
        communauto_id = "Label_8457010568994296209"
        credit_id = "Label_1667435912147980212"
        rbc_id = "Label_3358910350676290351"
        offers_id = "Label_426101741412861469"
        wise_id = "Label_4925215570237948792"
        security_id = "Label_5151399784548708030"
        bills_id = "Label_3898552857053985684"
        action_req_id = "Label_7412877949105455075"


        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            maxResults=500,
            q=query_email,
            includeSpamTrash="false"
        ).execute()
        # results = {
        #   "messages": [
        #     {
        #       object (Message)
        #     }
        #   ],
        #   "nextPageToken": string,
        #   "resultSizeEstimate": integer
        # }
        # where Message:
        #   "id": string,
        #   "threadId": string,
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
                q=query_email,
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
                      "addLabelIds": bills_id,
                      "removeLabelIds": [action_req_id, "INBOX", phone_id]
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