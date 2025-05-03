import base64
import quopri
import base64
import re
from bs4 import BeautifulSoup


def extract(results, extracted_emails):
    extracted_email = {}
    # extract id
    message_id = results.get('id')
    extracted_email['id'] = message_id

    # extract labels
    labels = results.get('labelIds')
    for label in labels:
        if label.startswith("Label"):
            extracted_email['label'] = label

    # extract subject
    payload = results.get("payload")
    headers_list = payload.get("headers")
    for entry in headers_list:
        if entry.get("name") == "Subject":
            extracted_email["Subject"] = entry.get("value")

    # extract text
    get_data(extracted_email, payload)

    extracted_emails['emails'].append(extracted_email)
    return extracted_emails


def get_data(extracted_email, payload):
    if "parts" not in payload:
        if 'data' in payload.get("body"):
            if payload.get("body")["data"] and payload.get("mimeType") == "text/plain":
                extracted_email['text'] = clean(base64.urlsafe_b64decode(payload.get("body").get("data", ""))
                                                .decode('utf-8', errors='replace')
                                                + " " + extracted_email.get('text', ''))
            elif payload.get("body")["data"] and payload.get("mimeType") == "text/html":
                html_content = (base64.urlsafe_b64decode(payload["body"].get("data", ""))
                                .decode("utf-8", errors="replace"))
                soup = BeautifulSoup(html_content, "html.parser")
                extracted_email['text'] = (clean(soup.get_text(separator="\n", strip=True))
                                           + " " + extracted_email.get('text', ''))

    if payload.get('parts'):
        for part in payload.get('parts'):
            get_data(extracted_email, part)


def clean(text):
    # remove newline and carriage return characters
    cleaned = text.replace('\n', ' ').replace('\r', ' ')
    # normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'‌', ' ', cleaned).strip()

    return cleaned
