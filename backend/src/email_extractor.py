import base64
import re

import unicodedata
from bs4 import BeautifulSoup
from .global_store import get_label_name
from datetime import datetime


def extract_message(result, data):
    # data = {
    #     "id": [],
    #     "from": [],
    #     "date": [],
    #     "label": [],
    #     "subject": [],
    #     "text": []
    # }

    # see data/raw/sample-email.json for more detail
    # result = {
    #     "id": string,
    #     "threadId": string,
    #     "labelIds": [
    #         string
    #     ],
    #     "snippet": string,
    #     "historyId": string,
    #     "internalDate": string,
    #     "payload": {
    #         object(MessagePart)
    #     },
    #     "sizeEstimate": integer,
    #     "raw": string
    # }

    # extract id
    email_id = result.get('id')
    data['id'].append(email_id)

    # extract date
    internal_date = result.get('internalDate')
    formatted_date = datetime.fromtimestamp(int(internal_date) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    data['date'].append(formatted_date)

    # extract labels
    # labels = result.get('labelIds')
    # appended = False
    # for label in labels:
    #     if label.startswith("Label"):
    #         data['label'].append(get_label_name(label))
    #         appended = True
    # if not appended:
    #     data['label'].append("Dummy label")

    # extract From, Subject
    payload = result.get("payload")
    headers_list = payload.get("headers")
    appended_subject = False
    appended_from = False
    for entry in headers_list:
        if entry.get("name") == "From" and not appended_from:
            data['from'].append(entry.get("value", 'Sender missing'))
            appended_from = True

        if entry.get("name") == "Subject" and not appended_subject:
            data['subject'].append(entry.get("value", 'Subject missing'))
            appended_subject = True

    if not appended_subject:
        data['subject'].append('Subject missing')
    if not appended_from:
        data['from'].append('Sender missing')

    # extract text
    text = get_text(payload)
    data['text'].append(text)

    if not (len(data['text']) == len(data['subject']) == len(data['id']) == len(data['date']) == len(data['from'])):
        print("Error id: ", email_id)
        print(len(data['text']))
        print(len(data['subject']))
        # print(len(data['label']))
        print(len(data['id']))
        print(len(data['date']))
        print(len(data['from']))
        raise Exception

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
            text = get_text(part) + text

    return text


def clean(text):
    # Normalize Unicode (NFKC = compatibility form, e.g., full-width -> half-width)
    text = unicodedata.normalize("NFKC", text)
    # Replace all Unicode spaces with regular spaces
    text = ''.join(' ' if unicodedata.category(c) == 'Zs' else c for c in text)
    # Explicitly replace NBSPs and zero-width characters
    text = text.replace('\u00A0', ' ').replace('\xa0', ' ').replace('\u200c', '')
    # Remove all words that start with '\u'
    text = re.sub(r'(\\u\w+|\\x\w+|&#\w+)', '', text)
    # Collapse all kinds of whitespace into a single space
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
