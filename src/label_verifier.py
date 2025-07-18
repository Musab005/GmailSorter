def is_labelled(results):
    labels = results.get('labelIds')
    for label in labels:
        if label.startswith("Label"):
            return True
    return False


def is_unlabelled(results):
    labels = results.get('labelIds')
    for label in labels:
        if label.startswith("Label") or label == "INBOX":
            return False
    return True
