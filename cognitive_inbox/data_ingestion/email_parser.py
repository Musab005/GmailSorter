# cognitive_inbox/data_ingestion/email_parser.py

import os
import dateparser
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from cognitive_inbox import config
from cognitive_inbox.src.email_extractor import get_text

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


# DONE
def get_gmail_service():
    creds = None
    if os.path.exists(config.GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the new token
        with open(config.GOOGLE_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        print("Gmail service successfully created.")
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def get_label_map(service, user_id='me'):
    """
    Fetches all labels in the user's account and creates a mapping
    from label ID to label name.
    """
    try:
        results = service.users().labels().list(userId=user_id).execute()
        labels = results.get('labels', [])
        label_map = {label['id']: label['name'] for label in labels}
        print(f"Successfully fetched {len(label_map)} labels.")
        return label_map
    except HttpError as error:
        print(f"An error occurred while fetching labels: {error}")
        return {}


def list_message_ids(service, user_id='me', limit=None):
    if limit is None:
        max_results = 500
    else:
        max_results = limit
    try:
        response = (service.users().messages().list(
            userId=user_id,
            maxResults=max_results,
            includeSpamTrash=False).execute())
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        if limit is None:
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(
                    userId=user_id,
                    pageToken=page_token,
                    maxResults=500,
                    includeSpamTrash=False
                ).execute()
                if 'messages' in response:
                    messages.extend(response['messages'])
                else:
                    break
        print(f"Found a total of {len(messages)} message IDs.")
        return [msg['id'] for msg in messages]
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []


def parse_email(service, label_map, message_id, user_id='me'):
    """
    Fetches and parses a single email into a clean dictionary.

    Args:
        service: The authenticated Gmail service object.
        label_map: A dictionary mapping label IDs to names.
        message_id: The ID of the email to parse.
        user_id: The user's email address (default is 'me').
    """
    try:
        message = service.users().messages().get(
            userId=user_id,
            id=message_id,
            format='full').execute()

        # extract labels
        lids = message.get('labelIds', [])
        label_names = []
        appended = False
        for lid in lids:
            if lid.startswith("Label"):
                label_names.append(label_map.get(lid, f"lid not found! {lid}"))
                appended = True
        if not appended:
            label_names.append("INBOX")

        payload = message['payload']
        headers = payload['headers']

        subject = ""
        from_sender = ""
        msg_date = None

        for header in headers:
            if header['name'].lower() == 'subject':
                subject = header['value']
            elif header['name'].lower() == 'from':
                from_sender = header['value']
            elif header['name'].lower() == 'date':
                msg_date = dateparser.parse(header['value'])

        # extract body text
        body = get_text(payload)

        date_timestamp = int(time.mktime(msg_date.timetuple())) if msg_date else None

        return {
            'id': message['id'],
            'subject': subject.strip(),
            'from': from_sender.strip(),
            'date': date_timestamp,
            'labels': ", ".join(label_names),
            'body': body.strip()
        }
    except HttpError as error:
        print(f'An error occurred while parsing email {message_id}: {error}')
        return None


def safe_str(value):
    return str(value) if value is not None else "N/A"
