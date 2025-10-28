import requests
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("BITRIX24_WEBHOOK_URL")

def get_deals(category_id):
    _method = 'crm.deal.list.json'
    url = f'{webhook_url}{_method}'

    params = {
        'filter': {
            'CATEGORY_ID': category_id
        },
        # 'select': ['ID', 'TITLE', 'CATEGORY_ID']
    }

    response = requests.post(url, json=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def get_deal_by_id(deal_id):
    _method = 'crm.deal.get.json'
    url = f'{webhook_url}{_method}'

    # Параметри запиту
    params = {
        'id': deal_id
    }

    # Виконуємо GET-запит до API Bitrix24
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None



def add_deal(
    title,
    category_id, # Заявки на еквайрінг - 4 | YouControl Нові фопи - 22
    type=None,
    storage_id=None, # Oschad - `C4:PREPARATION`, A-Bank - `C4:UC_6J54TL`, "Принать в роботу"  - `C22:UC_UUNHY5`  змінено з `C16:NEW`
    owner_name = None,
    owner_tel = None,
    name_aplication = None,
    tin_edrpou = None,
    legal_name=None,
    legal_address_city=None,
    legal_address_street=None,
    region_name = None,
    detail_region_name=None,
    company_name = None,
    place_name=None,
    regional_admin = None,
    company_address = None,
    bank_name = None,
    bank_initials = None,
    bank_manager = None,
    tel_bank_employee=None,
    tel_cashier = None,
    terminal_id=None,
    merchant_id=None,
    contact_id=None,
    company_id=None,
    amount=None,
    comments=None,
    bank_tp=None,
    mss=None,
    trading_name=None,

    serial_number = None,
    source_id = None
    ):
    
    print("Add deal", title, category_id, storage_id, source_id)

    _method = 'crm.deal.add.json'
    url = f'{webhook_url}{_method}'
    addres_company_full = f'{region_name if region_name else ""} {detail_region_name if detail_region_name else ""}'.strip()

    params = {
        'fields': {
            'TITLE': title,
            'CATEGORY_ID': category_id,
            'STAGE_ID':storage_id,
            'UF_CRM_1716916242':type,


            'CONTACT_ID': contact_id,
            'COMPANY_ID': company_id,
            'OPPORTUNITY': amount,

            # 'UF_CRM_1683118575':legal_name,
            'UF_CRM_1683118575':company_name,
            'UF_CRM_1682949247':addres_company_full,

            # 'UF_CRM_1682949230': f'{trading_name if trading_name else ""} {place_name if place_name else ""}',
            'UF_CRM_1682949230': f'{place_name if place_name else ""}',
            
            'UF_CRM_1682949203':tin_edrpou,
            'UF_CRM_1682949301':merchant_id,
            'UF_CRM_1682949378':terminal_id,
            'UF_CRM_1682949121':regional_admin,

            'UF_CRM_1682949511':bank_initials,
            'UF_CRM_1682949965':bank_manager,
            'UF_CRM_1683011059':tel_bank_employee,
            'UF_CRM_1682949098':bank_tp, # Oshad : 48, A-bank: 82
            'UF_CRM_1682949511':bank_name,

            'UF_CRM_1682949214':mss,
            'UF_CRM_1683034080':tel_cashier,

            'COMMENTS':comments,

            'UF_CRM_1717154296' : owner_name,
            'UF_CRM_1717154315' : owner_tel,

            'UF_CRM_1683011081' : serial_number,
            "SOURCE_ID" : source_id
        }
    }

    response = requests.post(url, json=params)
    if response.status_code == 200:
        print("Add deal success", title)
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None
    
# a = add_deal(title="НЕ ВИДАЛЯТИ. TEST", category_id=4, tin_edrpou=00000000, comments='тестуєм підключення', storage_id="C4:PREPARATION")
# deals_list = get_deals(4) 
# deals_list = get_deal_by_id(142506)
# print(deals_list)
# print(a)
