import pickle
from gmail_client import GmailClient
from email.mime.text import MIMEText
import base64
import sys


ACCESS_TOKEN_FILE = "token.pickle"


def create_message(message):
    mime_msg = MIMEText(message.get('text', "No Message"))
    mime_msg['to'] = 'amythcloud@gmail.com'
    mime_msg['from'] = 'postamyth@gmail.com'
    mime_msg['subject'] = message['subject']
    return {'raw': base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()}


# start from 914.

if __name__ == "__main__":
    credential = None
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        credentials = pickle.load(tf)
    gmc = GmailClient()
    label_ids = ['Label_8904163162243193684']

    count = 0
    first = True
    while first or next_page_token:
        if first:
            messages, next_page_token = gmc.list_emails_by_labels(
                                        label_ids=label_ids)
        else:
            messages = gmc.list_emails_by_labels(
                            label_ids=label_ids,
                            page_token=next_page_token)

        for m in messages:
            if count <= 914:
                print("Message already sent")
                continue
            gmc.send_mail(create_message(m))
            count += 1
            print(f"Sent message no {count}")
