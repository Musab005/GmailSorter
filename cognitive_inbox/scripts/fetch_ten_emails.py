import json
import os.path
from googleapiclient.errors import HttpError

from cognitive_inbox.data_ingestion.email_parser import get_gmail_service, parse_email, get_label_map, list_message_ids

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    cog_inbox_dir = os.path.dirname(scripts_dir)
    root_dir = os.path.dirname(cog_inbox_dir)
    data_path = os.path.join(root_dir, "data")
    service = get_gmail_service()
    label_map = get_label_map(service)
    if service:
        try:
            message_ids = list_message_ids(service, limit=10)
            for message_id in message_ids:
                parsed_email_map = parse_email(service, label_map, message_id)
                with open(f"{data_path}\{message_id}.json", "w") as f:
                    json.dump(parsed_email_map, f, indent=4)
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None


if __name__ == "__main__":
    main()
