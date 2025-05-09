import base64
import re

import unicodedata
from bs4 import BeautifulSoup


## to csv
#
# # Example data
# data = {
#     "text": ["email 1 content", "email 2 content"],
#     "label": ["work", "personal"]
# }
#
# df = pd.DataFrame(data)
#
# # Write to CSV
# df.to_csv("emails.csv", index=False, encoding="utf-8")


def extract_message(results, data):
    # data = {
    #     "id": [],
    #     "label": [],
    #     "subject": [],
    #     "text": []
    # }

    # extract id
    email_id = results.get('id')
    data['id'].append(email_id)

    # extract labels
    labels = results.get('labelIds')
    appended = False
    for label in labels:
        if label.startswith("Label"):
            data['label'].append(label)
            appended = True
    if not appended:
        data['label'].append("Dummy text")

    # extract subject
    payload = results.get("payload")
    headers_list = payload.get("headers")
    for entry in headers_list:
        if entry.get("name") == "Subject":
            data['subject'].append(entry.get("value"))
    if not data['subject']:
        data['subject'].append("Dummy text")

    # extract text
    text = get_text(payload)
    data['text'].append(text)

    return


def get_text(payload):
    text = ""
    if "parts" not in payload:
        if 'data' in payload.get("body"):
            if payload.get("mimeType") == "text/plain":
                # extract
                # NOTE: base64.urlsafe_b64decode() returns a bytes object. Need to convert to string
                decoded_bytes = base64.urlsafe_b64decode(payload.get("body").get("data", ""))
                cleaned_text = clean(decoded_bytes.decode("utf-8", errors="ignore"))
                # return
                return cleaned_text + text
            elif payload.get("mimeType") == "text/html":
                # extract
                decoded_bytes = base64.urlsafe_b64decode(payload.get("body").get("data", ""))
                cleaned_html = clean(decoded_bytes.decode("utf-8", errors="ignore"))
                soup = BeautifulSoup(cleaned_html, "html.parser")
                raw_html = soup.get_text()
                return clean(raw_html + text)

    if payload.get('parts'):
        for part in payload.get('parts'):
            text = get_text(part)

    return text


def clean(text):
    # Normalize Unicode (NFKC = compatibility form, e.g., full-width -> half-width)
    text = unicodedata.normalize("NFKC", text)
    # Replace all Unicode spaces with regular spaces
    text = ''.join(' ' if unicodedata.category(c) == 'Zs' else c for c in text)
    # Explicitly replace NBSPs and zero-width characters
    text = text.replace('\u00A0', ' ').replace('\xa0', ' ').replace('\u200c', '')
    # Collapse all kinds of whitespace into a single space
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
