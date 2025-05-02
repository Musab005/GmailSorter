import base64
import quopri
import base64
import quopri
import binascii  # Explicitly import binascii


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

    # save extracted email
    # extracted_email['text'] = (
    #     base64.urlsafe_b64decode(extracted_email.get('text', '')).decode('utf-8', errors='replace')
    #     .replace('\r', '').replace('\n', ''))

    extracted_emails['emails'].append(extracted_email)
    return extracted_emails


def get_data(extracted_email, payload):
    if "parts" not in payload:
        if 'data' in payload.get("body"):
            if payload.get("body")["data"] and payload.get("mimeType") == "text/plain":
                # extracted_email['text'] =  + " " + extracted_email.get('text', '')
                extracted_email['text'] = ((base64.urlsafe_b64decode(payload.get("body")["data"])
                                           .decode('utf-8', errors='replace').replace('\r', '')
                                           .replace('\n', ''))
                                           + " " + extracted_email.get('text', ''))
            elif payload.get("body")["data"] and payload.get("mimeType") == "text/html":
                try:
                    decoded_data = base64.urlsafe_b64decode(payload.get("body")["data"])
                    decoded_text = decoded_data.decode('utf-8', errors='replace')
                except (base64.binascii.Error, UnicodeDecodeError):
                    # Fallback to quopri if it's not base64-encoded
                    decoded_text = quopri.decodestring(payload.get("body")["data"]).decode('utf-8', errors='replace')
                extracted_email['text'] = decoded_text + " " + extracted_email.get('text', '')
                # extracted_email['text'] = (quopri.decodestring(payload.get("body")["data"]).decode('utf-8')
                #                            + " " + extracted_email.get('text', ''))
    if payload.get('parts'):
        for part in payload.get('parts'):
            get_data(extracted_email, part)