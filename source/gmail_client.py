import google.oauth2.credentials
import googleapiclient.discovery
import preprocessor
import pickle

from apiclient import errors
from base64 import urlsafe_b64decode
from logger import logger

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

CLIENT_SECRETS_FILE = "client_secret.json"
ACCESS_TOKEN_FILE = "token.pickle"


class GmailClient:
    def __init__(self):
        self._credentials = None
        with open(ACCESS_TOKEN_FILE, "rb") as tf:
            token = pickle.load(tf)
            self._credentials = google.oauth2.credentials.Credentials(
                                **token)

    def get_credentials(self):
        return self._credentials

    def list_labels(self):
        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self.get_credentials())
        results = gmail.users().labels().list(userId='me').execute()
        return results

    def list_emails(self, label_ids=None, page_token=None):
        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self.get_credentials())
        # TODO: does not declaring "results" outside of "if" work?
        if not page_token:
            results = gmail.users().messages().list(
                userId='me',
                labelIds=label_ids).execute()
        else:
            results = gmail.users().messages().list(
                userId='me',
                labelIds=label_ids,
                pageToken=page_token).execute()
        logger.debug(f"Fetched {len(results.get('messages', list()))}.")
        logger.debug(f"Page token {results.get('nextPageToken', None)}")
        # parse each message and create a new list.
        messages = list()
        for message in results['messages']:
            logger.debug(f"Downloading message Id {message['id']}.")
            messages.append(self.get_message(message['id']))

        return messages, results.get('nextPageToken', None)

    def list_mails_with_subjects_only(self, label_ids=None, page_token=None):
        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self.get_credentials())

        results = gmail.users().messages().list(
                userId='me',
                labelIds=label_ids,
                pageToken=page_token).execute()

        logger.info(results.get("resultSizeEstimate", "Unknown"))
        return results.get('messages', list()), results.get('nextPageToken', None)

    @staticmethod
    def _parse_msg(msg):
        # construct our message structure.
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

        # capture text from all the parts.
        part_queue = list()
        parts = payload.get("parts", list())
        logger.info(f"No of parts: {len(parts)}")
        part_queue.extend(parts)
        while len(part_queue) > 0:
            part = part_queue.pop(0)
            mime_type = part.get("mimeType", "")
            logger.info(f"MimeType: {mime_type}")
            body = part.get("body", None)
            if body is None:
                # TODO log info.
                continue
            data = body.get("data", "")
            size = int(body.get("size", 0))
            if mime_type == "text/plain":
                if data != "":
                    text = urlsafe_b64decode(data).decode()
                    text = preprocessor.preprocess_html(text)
                    # accumulate text
                    parsed_msg["text"] = parsed_msg.get("text", "") + text
            elif mime_type == "text/html":
                html = urlsafe_b64decode(data).decode()
                text = preprocessor.preprocess_html(html)
                parsed_msg["text"] = parsed_msg.get("text", "") + text
            else:
                # TODO parse attachments
                pass
            # check if there are nested parts.
            if part.get("parts", None):
                # nested parts
                nested_parts = part.get("parts")
                part_queue.extend(nested_parts)
        return parsed_msg

    def get_message(self, msg_id):
        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self.get_credentials())
        raw_msg = gmail.users().messages().get(userId='me', id=msg_id).execute()
        logger.debug(f"Downloaded message {msg_id}.")
        return GmailClient._parse_msg(raw_msg)

    def send_mail(self, message):
        try:
            gmail = googleapiclient.discovery.build(
                API_SERVICE_NAME,
                API_VERSION,
                credentials=self.get_credentials())
            gmail.users().messages().send(userId='me', body=message).execute()
        except errors.HttpError as error:
            print('An error occurred: %s' % error)


if __name__ == "__main__":
    import json
    gmc = GmailClient()
    labels = gmc.list_labels()['labels']
    print(type(labels))
    print(next(filter(lambda x: x.get('name', "") == "cs410", labels)))
