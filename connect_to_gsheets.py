from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = './cred.json'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



def get_values_from_sheet(SPREADSHEET_ID, RANGE_NAME):
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Виклик API для отримання значень
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Data from sheet:')
        for row in values:
            print(row)

def append_row_to_sheet(values, SPREADSHEET_ID, RANGE_NAME):
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Виклик API для додавання нового рядка
    body = {
        'values': values
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',  # Вставляє нові рядки
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells appended.")

if __name__ == '__main__':
    exec
    # get_values_from_sheet('1QK75bz7KmLEIuDRI89_2XD0TQXqQ-LJ4D8DQ7ijJSm0', 'A1:D10')
    # append_row_to_sheet(values,"1dgbTY-_aj4bwkdWjy821uK7aDh0SqEYVU3GHhVE2jpI", 'Лист1')
