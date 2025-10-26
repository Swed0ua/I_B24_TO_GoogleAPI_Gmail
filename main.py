import time
import traceback
from connect_to_crm import add_deal
from connect_to_gapi import get_new_messages, get_service
from types_file import BANK_NAMES, MAIL_NAMES

# TODO: Temporary stoped
# from config import A_BANK_CONF, OSCHAD_CONF
# from connect_to_gsheets import append_row_to_sheet
# def append_oshad_data_in_gsheets(body):
#     append_row_to_sheet([body], OSCHAD_CONF["gsheets_id"], OSCHAD_CONF["range"])
# def append_abank_data_in_gsheets(body):
#     append_row_to_sheet([body], A_BANK_CONF["gsheets_id"], A_BANK_CONF["range"])
   

def program():
    service = get_service()
    messages = get_new_messages(service, query='is:unread')
    for message in messages:
        parce_body = message[0]
        bank_tp = message[1]

        bank_acquiring = ''
        
        if BANK_NAMES.OSCHAD == bank_tp:
            bank_acquiring = 'АТ "Ощадбанк"'
            legal_address = f"{parce_body['legal_address_city'] if parce_body['legal_address_city'] else '' } {parce_body['legal_address_street'] if parce_body['legal_address_street'] else ''}"
            addres_company_full = f'{parce_body["region_name"] if parce_body["region_name"] else ""} {parce_body["detail_region_name"] if parce_body["detail_region_name"] else ""}'


            # TODO: Temporary stoped
            # review_data = [bank_acquiring, parce_body['type'], parce_body["region_name"], parce_body["tin_edrpou"], legal_address, parce_body["place_name"], addres_company_full, parce_body["merchant_id"], parce_body["terminal_id"], parce_body["owner_name"], parce_body["owner_tel"], bank_acquiring, parce_body["bank_manager"], parce_body["tel_bank_employee"], parce_body["comments"], parce_body["type"]]
            # append_oshad_data_in_gsheets(review_data)
            
            add_deal(**parce_body, title=parce_body["type"], category_id=4, storage_id="C4:PREPARATION", bank_tp=48, bank_name=bank_acquiring)
        if BANK_NAMES.ABANK == bank_tp:
            bank_acquiring = 'А-Банк'
            add_deal(**parce_body, title=parce_body["type"], category_id=4, storage_id="C4:UC_6J54TL", bank_tp=82, bank_name=bank_acquiring)
        if MAIL_NAMES.SMARTKASA == bank_tp:
            add_deal(**parce_body, title=parce_body["type"], category_id=22, storage_id="C22:UC_UUNHY5", source_id="EMAIL")
            # add_deal(**parce_body, title="TEST | розробка | Не видаляти", category_id=16, storage_id="C16:NEW", source_id="EMAIL")

if __name__ == '__main__':
    while True:

        try:
            program()
        except Exception as e:
            traceback.print_exc()
            print(f'error | {type(e).__name__} | {e}')

        time.sleep(60)