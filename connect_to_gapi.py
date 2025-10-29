import asyncio
import base64
import json
import os.path
import pickle
import time
from bs4 import BeautifulSoup
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery

# from connect_to_crm import add_deal
from functions import parce_NRP_smartkasa_ua_mail, parce_abank_mail, parce_oshad_mail
from tg_bot_sender import send_message_to_group, send_message_to_group_bank_supports, send_message_to_group_bot2, send_message_to_group_service_support, GROUP_СASH_REGISTER
from types_file import BANK_NAMES, MAIL_NAMES

# Області доступу
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = './client_secret.json'
TOKEN_FILE = 'token.pickle'

def get_service():
    creds = None
    # Перевірка наявності збережених облікових даних
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Якщо облікових даних немає або вони недійсні, виконуємо процес входу
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Зберігаємо облікові дані для наступного використання
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    return service

def get_html_body_with_mail(msg):
    html_body = None
    isHtml = None

    def procPartIter(part):
        body_data = part['body']['data']
        body_bytes = base64.urlsafe_b64decode(body_data.encode('UTF-8'))
        return body_bytes.decode('UTF-8')


    if 'parts' in msg['payload']:
        isHtml = True
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/html':
                # body_data = part['body']['data']
                # body_bytes = base64.urlsafe_b64decode(body_data.encode('UTF-8'))
                # html_body = body_bytes.decode('UTF-8')

                html_body = procPartIter(part)
                break
    else :
        part = msg['payload']
            
        html_body = procPartIter(part)
    return [html_body, isHtml]

def set_read_status(service, message):
    service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

def separate_html_to_text(html:str):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator="")
    return text.strip()

def get_bank_type_from_subject(text:str):
    bank_names = {
        "ОЩАДБАНК": BANK_NAMES.OSCHAD,
        "ПУМБ Банк": BANK_NAMES.PUMB,
        "БАНК ПІВДЕННИЙ": BANK_NAMES.PIVDENNUY,
        "ОКСІ БАНК": BANK_NAMES.OKSI,
        "РАЙФАЙЗЕНК БАНК АВАЛЬ": BANK_NAMES.RAIFF,
        "А БАНК": BANK_NAMES.ABANK,
        "БАНК ВОСТОК": BANK_NAMES.VOSTOK,
    }

    for bank_name, bank_type in bank_names.items():
        if bank_name in text:
            return bank_type
    return None

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def should_process_email(bank_type, subject):
    """
    Повертає True, якщо лист потрібно обробити відповідно до правил.
    """
    if "Зміна шапки чеку" in subject:
        return True

    if bank_type == BANK_NAMES.PUMB:
        return "Смарт каса заміна серійного номеру ПУМБ Банк" in subject

    return "Власник бізнесу хоче відновити" in subject


def get_new_messages(service, query=''):
    http = service._http
    http.timeout = 20  
    results = service.users().messages().list(userId='me', q=query).execute(http=http)
    messages = results.get('messages', [])

    result_list = []
    if not messages:
        print('...')
        exec
    else:
        print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            message_id = msg['id']
            
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)

            print("sender-",sender.strip())
            print("subject-",subject.strip())

            if "Заявка з бота  AI- менеджер підтримки" in subject:
                try:
                    [html_body, isHtml] = get_html_body_with_mail(msg)
                    if not html_body : continue
                    html_body = html_body.replace("<br>", "\n").replace("&nbsp;", " ")

                    loop.run_until_complete(send_message_to_group_service_support(html_body))
                
                except Exception as e:
                    print('Error', e)

            if sender.strip()=='"Ощадбанк Контакт-центр" <contact-centre@oschadbank.ua>':
                html_body = get_html_body_with_mail(msg)
                if not html_body : continue
                parce_body = parce_oshad_mail(html_body[0])

                print(parce_body)

                result_list.append([parce_body, BANK_NAMES.OSCHAD])

                # add_deal(**parce_body, title='Test | 3', category_id=4, storage_id="C4:PREPARATION", bank_tp=48)
                set_read_status(service, message)
            elif sender.strip() == '"smart.kasa office" <smart.kasa.office@smartkasa.ua>' or sender.strip() == 'pos.mail@a-bank.com.ua' or sender.strip() == '"office smart.kasa" <smart.kasa.office@smartkasa.ua>':
                [html_body, isHtml] = get_html_body_with_mail(msg)
                if not html_body : continue

                parce_body = parce_abank_mail(html_body, isHtml)
                parce_body['type'] = subject
                result_list.append([parce_body, BANK_NAMES.ABANK])

                set_read_status(service, message)
            elif sender.strip() == "noreply@smartkasa.ua":
                try:
                    [html_body, isHtml] = get_html_body_with_mail(msg)
                    if not html_body : continue

                    if "Заявка на підтримку" in subject:
                        html_body = html_body.replace("<p>", "").replace("</p>", "\n")
                        loop.run_until_complete(send_message_to_group_service_support(html_body))
                    else:
                        parce_body = parce_NRP_smartkasa_ua_mail(html_body, isHtml)
                        parce_body['type'] = subject
                        result_list.append([parce_body, MAIL_NAMES.SMARTKASA])
                    
                    set_read_status(service, message)
                except Exception as e:
                    print('Error', e)
            elif sender.strip() == '"Юрій Федоран" <no-reply@smartkasa.bitrix24.eu>':                
                try:
                    [html_body, isHtml] = get_html_body_with_mail(msg)
                    if not html_body : continue
                    html_body = html_body.replace("<br>", "\n").replace("&nbsp;", " ")

                    if "Заміна смарт каси" in subject:
                        new_text = separate_html_to_text(html_body)
                        loop.run_until_complete(send_message_to_group_bot2(new_text, group_id=GROUP_СASH_REGISTER))
                    elif "Потрібно рахунок" in subject:
                        loop.run_until_complete(send_message_to_group(html_body))

                except Exception as e:
                    print('Error', e)
            elif sender.strip() == '"Юрій Федоран" <no-reply@smartkasa.bitrix24.eu>':                
                try:
                    [html_body, isHtml] = get_html_body_with_mail(msg)
                    if not html_body : continue
                    html_body = html_body.replace("<br>", "\n").replace("&nbsp;", " ")
                    
                    bankType = None

                    # if "Смарт каса заміна серійного номеру" in subject:
                    #     bankType = BANK_NAMES.PUMB
                    # else:
                    
                    bankType = get_bank_type_from_subject(subject)

                    if bankType:
                        print("bankType: ", bankType)
                        # is_procces = True 

                        # # обробник виключень
                        # if bankType == BANK_NAMES.PUMB and not "Смарт каса заміна серійного номеру ПУМБ Банк" in subject:
                        #     is_procces = False

                        # if bankType != BANK_NAMES.PUMB and not "Власник бізнесу хоче відновити" in subject:
                        #     is_procces = False
                        
                        if should_process_email(bank_type=bankType, subject=subject):
                            loop.run_until_complete(send_message_to_group_bank_supports(html_body, bankType))
                
                except Exception as e:
                    print('Error', e)
            elif sender.strip() == '"Смарт каса - Офіс" <smart.kasa.office@smartkasa.ua>':       
                try:
                    [html_body, isHtml] = get_html_body_with_mail(msg)
                    if not html_body : continue
                    html_body = html_body.replace("<br>", "\n").replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")

                    if "Потрібно рахунок" in subject:
                        loop.run_until_complete(send_message_to_group(html_body))

                except Exception as e:
                    print('Error', e)

            # TODO 
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    return result_list

def main():
    service = get_service()
    get_new_messages(service, query='is:unread')

if __name__ == '__main__':
    main()
