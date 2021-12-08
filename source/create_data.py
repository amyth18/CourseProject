import base64
from email.mime.multipart import MIMEMultipart
from gmail_client import GmailClient


def create_message(msg):
    parsed_msg = dict()
    parsed_msg["messageId"] = msg["id"]
    parsed_msg["labels"] = msg["labelIds"]
    # all the stuff is in the payload.
    payload = msg['payload']
    # TODO payload has a body element, will it have text element?
    # extract only the required headers.
    headers = payload.get("headers", list())
    for header in headers:
        name = header.get("name", "")
        value = header.get("value", "")
        if name.lower() == "from":
            parsed_msg["from"] = value
        elif name.lower() == "subject":
            parsed_msg["subject"] = value

    message = MIMEMultipart()
    message['to'] = "amythcloud@gmail.com"
    message['from'] = parsed_msg["from"]
    message['subject'] = parsed_msg["subject"]
    message.set_payload(payload)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


if __name__ == "__main__":
    gmc = GmailClient()
    label_ids = ['Label_8904163162243193684']

    count = 0
    first = True
    next_page_token = None

    while first or next_page_token:
        messages, next_page_token = gmc.list_mails_with_subjects_only(
                        label_ids=label_ids,
                        page_token=next_page_token)
        with open("send.log", "w") as sfd:
            for m in messages:
                raw_msg = gmc.get_message(m['id'], raw=True)
                gmc.send_mail(create_message(raw_msg))
                count += 1
                print(f"Sent message no {count}")
                break

        next_page_token = None
        first = False
