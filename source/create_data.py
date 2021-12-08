import base64
import random
import pandas as pd
from email.mime.text import MIMEText

from gmail_client import GmailClient
from mongo_client import MongoDBClient


def create_message(msg):
    message = MIMEText(msg.text)
    message['to'] = "amythcloud@gmail.com"
    message['from'] = "postamyth@gmail.com"
    message['subject'] = msg.subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        'raw': raw_message.decode("utf-8")
    }


if __name__ == "__main__":
    gmc = GmailClient()
    mdb = MongoDBClient()
    count = 0
    first = True
    mail_df = mdb.get_all_messages()
    random_ids = random.sample(range(0, 2885), 800)

    with open("send.log", "w") as sfd:
        for idx in range(len(mail_df)):
            if idx not in random_ids:
                continue
            r = mail_df.loc[idx]
            if str(r['from']).find("apartmentadda") >= 0 or \
                    pd.isna(r['text']):
                continue
            gmc.send_mail(create_message(r))
            count += 1
            print(f"Sent message no {count}")

