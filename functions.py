import json
import time
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()

key_val = {
    "Тип заявки" : "type",
    "Ім'я заявки":"name_aplication",
    "Інформація по ТСП ПІБ директора" : "owner_name",
    "Інформація по ТСП Телефон директора" : "owner_tel",
    # "Номер договору" : "",
    "Відповідальна особа за роботу еквайрингу" : "bank_manager",
    "Інформація по ТСП Мобільний телефон особи від ТСП":"tel_bank_employee",
    "ЄДРПОУ/ІПН" : "tin_edrpou",
    "Інформація по ТСП Юридична назва ТСП":"company_name",
    "Інформація по ТСП Контактний телефон особи від ТСП":"tel_cashier",
    "Контактний телефон":"tel_cashier_add",
    "ContractNumber (MerchaintID)":"merchant_id",
    "ContractNumber(Terminal)": "terminal_id",
    "Адреса місця торгівлі / послуг Вулиця, будинок":'company_address',
    "Адреса місця торгівлі / послуг Місто":"region_name",
    "Адреса місця торгівлі / послуг Вулиця, будинок":"detail_region_name",
    "SIC Код":"mss",
    "Регіональне управління":"regional_admin",
    "Назва торгівельної мережі":"trading_name",
    "Назва місця торгівлі / послуг (держ. мовою)":"place_name",
    "Юридична адреса Місто":"legal_address_city",
    "Юридична адреса Вулиця":"legal_address_street",
    "Коментар":"comments",
    "Серійний номер Смарт каси":"serial_number",
    "contact_id":"contact_id"
    # "source_id":"source_id"
}

key_val_abanl = {
    # "bank" : "А-Банк",
    "inn_or_okpo" : "tin_edrpou",
    "merchant_name" : "company_name",
    "trade_point_name" : "place_name",
    "trade_point_address" : "detail_region_name",
    "retail_id" : "mss",
    "terminal_id" : "terminal_id",
    "merchant_id" : "merchant_id",
    "merchant_fio" : "owner_name",
    "merchant_phone" : "owner_tel"
}

key_val_smartkasa_mobile = {
    # "Серійний номер" : "serial_number"
}

def create_default_data(iter=key_val):
    res = {}
    for key, val in iter.items():
        res[val] = None
    return res

def parce_oshad_mail(txt:str):
    res = create_default_data()

    parsed_html_body = BeautifulSoup(txt.replace('&nbsp;', ' ').strip(), 'html.parser')
    parsed_html_body_elements = parsed_html_body.findAll('div')
    for element in parsed_html_body_elements:
        # print(element.text)
        try:
            # element_obj = element.text.strip().split(':')
            # element_key = element_obj[0].strip()
            # element_val = element_obj[-1]
            # element_key = element_key
            # if element_key in key_val:
            #     res[key_val[element_key]] = element_val.strip()

            element_obj = element.text.replace("  ", " ").strip().split(':')
            element_key = element_obj[0].strip()
            element_val = element_obj[-1].strip()

            for key in key_val:
                if key in element_key:
                    res[key_val[key]] = element_val
                    break 
                
        except:
            exec
    # time.sleep(1000)

    if res["tel_cashier"] is None:
        res["tel_cashier"] = res['tel_cashier_add']
    del res["tel_cashier_add"]

    id = get_contact_id(first_name=res["owner_name"], phone=res["tel_cashier"], email=None)
    res['contact_id'] = id

    return res



def parce_abank_mail(txt:str, isHtml=True):
    if isHtml:
        parsed_html_body = BeautifulSoup(txt.replace('&nbsp;', ' ').strip(), 'html.parser')
        parsed_html_body_elements = parsed_html_body.find('p', class_='MsoNormal').find('span')

        text_content = ' '.join(parsed_html_body_elements.stripped_strings)
    else:
        text_content = txt

    res = create_default_data()

    try:
        # print(text_content.split('--')[0])
        obj_content = f"{text_content.split('--')[0].strip()}"
        json_object = json.loads(obj_content)
        print(json_object["bank"])

        for key, val in json_object.items():
            if key in key_val_abanl:
                res[key_val_abanl[key]] = val.strip()
        

        id = get_contact_id(first_name=res["owner_name"], phone=res["owner_tel"], email=None)
        res['contact_id'] = id

    except Exception as e:
        print('Error', e)
    print(res)

    if "tel_cashier_add" in res:
        del res["tel_cashier_add"]
    
    return res


webhook_url = os.getenv("BITRIX24_WEBHOOK_URL")


def get_contact_id_by_number(number):
    _method = 'crm.contact.list.json'
    url = f'{webhook_url}{_method}'

    data = {
        'filter': {
            'PHONE': number
        },
        'select': ['ID']
    }

    response = requests.post(url, json=data)
    result = response.json()

    return result['result']

def create_contact(first_name=None, last_name=None, phone=None, email=None):
    _method = 'crm.contact.add.json'
    url = f'{webhook_url}{_method}'

    data = {
        'fields': {
            'NAME': first_name,
            'LAST_NAME': last_name,
            'OPENED': 'Y',  # Відкритий для всіх
            'TYPE_ID': 'CLIENT',  # Тип контакту
            'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'WORK'}],  
            'EMAIL': [{'VALUE': email, 'VALUE_TYPE': 'WORK'}],  
        }    
    }

    response = requests.post(url, json=data)
    result = response.json()
    return result['result']


def get_contact_id(first_name=None, last_name=None, phone=None, email=None):
    is_ids = get_contact_id_by_number(phone)
    if len(is_ids)<=0:
        is_ids = create_contact(first_name, last_name, phone, email)
    else:
        is_ids = is_ids[0]['ID']
    print("is_ids",is_ids)
    return is_ids


def parce_NRP_smartkasa_ua_mail(txt:str, isHtml=True):
    res = create_default_data()
    new_res = {
    }

    parsed_html_body = BeautifulSoup(txt.replace('&nbsp;', ' ').strip(), 'html.parser')
    parsed_html_body_elements = parsed_html_body.findAll('p')

    for element in parsed_html_body_elements:
        element_arr = element.text.strip().split(':')
        key = element_arr[0]
        val = element_arr[-1]

        new_res[key] = val

        if key in key_val_smartkasa_mobile:
            res[key_val_smartkasa_mobile[key]] = val.strip()

    # id = get_contact_id(first_name=new_res["Ім'я"], phone=new_res["Телефон"], email=new_res["Email"])
    id = get_contact_id(first_name=new_res["Ім'я"], phone=new_res["Телефон"], email=None)
    res['contact_id'] = id

    if "tel_cashier_add" in res:
        del res["tel_cashier_add"]
    return res
