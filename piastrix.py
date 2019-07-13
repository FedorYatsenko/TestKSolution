import os
import json
import hashlib
import requests

# currencies = {
#     "EUR": 978,
#     "USD": 840,
#     "RUB": 643
# }


# def create_sign(amount, currency, payway, shop_id, shop_order_id):
#     s = str(amount) + ":" + str(currency) + ":"\
#         + payway + ":" + shop_id + ":"\
#         + str(shop_order_id) + os.environ['SecretKey']
#
#     hsh = hashlib.sha256(s.encode('utf-8')).hexdigest()
#
#     return hsh


def create_sign(*args):
    s = ""
    for arg in args:
        s += str(arg) + ":"

    s = s[:-1] + os.environ['SecretKey']

    hsh = hashlib.sha256(s.encode('utf-8')).hexdigest()

    return hsh


def send_json(data, invoice=False):
    if invoice:
        r = requests.post('https://core.piastrix.com/invoice/create', json=data)
    else:
        r = requests.post('https://core.piastrix.com/bill/create', json=data)

    # print(r.status_code)
    # print(r.headers)
    # print(r.content)
    # print(r.json())

    return r.json()


# def send(amount, currency, payway, shop_order_id, description):
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     payload = {
#         'amount': amount,
#         'currency': currencies[currency],
#         'shop_id': SHOP_ID,
#         'sign': create_sign(amount, currency, payway, SHOP_ID, shop_order_id),
#         'shop_order_id': shop_order_id,
#         'description': description
#     }
#
#     session = requests.Session()
#     r = session.post('https://pay.piastrix.com/ru/pay', headers=headers, data=payload)
#
#     if r.status_code == 200:
#         print(r.content)
#     else:
#         print(r.status_code)
#
#
# if __name__ == '__main__':
#     print(send(50.65, 643, "payeer_rub", 1, "Description"))
