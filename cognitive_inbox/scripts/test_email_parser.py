import json
import os.path
from googleapiclient.errors import HttpError

from cognitive_inbox.data_ingestion.email_parser import get_gmail_service, parse_email, get_label_map

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]


def main():
    message_id = "19824a09b838ebd3"
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    cog_inbox_dir = os.path.dirname(scripts_dir)
    root_dir = os.path.dirname(cog_inbox_dir)
    data_path = os.path.join(root_dir, "data")
    service = get_gmail_service()
    if service:
        try:
            parsed_email_map = parse_email(service, get_label_map(service), message_id)
            with open(f"{data_path}\email_parser_output.json", "w") as f:
                json.dump(parsed_email_map, f, indent=4)

        except HttpError as error:
            print(f'An error occurred while parsing email {message_id}: {error}')
            return None


if __name__ == "__main__":
    main()
