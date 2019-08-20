from __future__ import print_function

import time
import webbrowser
import pickle

from bs4 import BeautifulSoup
import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def verify_steam_email(service, msg_id):
    message = service.users().messages() \
        .get(userId='me', id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    soup = BeautifulSoup(msg_str, features='html.parser')

    # first link is the entire Steam HTML frame for the email display
    link = soup.findAll('a')[1].get('href')
    print(f'Opening \'{link}\'')
    # this will only work for macOS
    # check https://stackoverflow.com/a/24353812/6908755
    chrome_path = 'open -a /Applications/Google\\ Chrome.app %s'
    open_in_tab = 2
    webbrowser.get(chrome_path).open(link, open_in_tab, autoraise=False)


def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def main():
    service = get_gmail_service()
    query = \
        'from:(noreply@steampowered.com) ' \
        'subject:(Community Market Listing Confirmation)'
    messages = service.users().messages() \
        .list(userId='me', q=query) \
        .execute().get('messages')

    print(f'There are {len(messages)} market listings to confirm!')
    for msg in messages:
        verify_steam_email(service, msg["id"])
        time.sleep(2)


if __name__ == '__main__':
    main()
