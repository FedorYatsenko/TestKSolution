from datetime import datetime
from collections import deque
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from db import get_db
from piastrix import create_sign, send_json

bp = Blueprint('main', __name__)

currencies = {
    "EUR": 978,
    "USD": 840,
    "RUB": 643
}

SHOP_ID = "5"
PAY_WAY = "payeer_rub"


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        amount = request.form['amount']
        currency = request.form['currency']
        description = request.form['description']
        purchases_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error = None

        if not amount:
            error = 'Amount is required.'
        elif not currency:
            error = 'Currency is required.'
        elif not description:
            error = 'Description is required.'
        else:
            try:
                amount = float(amount)
            except ValueError as ex:
                error = '"{}" cannot be converted to an int: {}'.format(amount, ex)

        if error is not None:
            current_app.logger.warning('POST with error:{}'.format(error))
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO purchases (amount, currency, description, purchases_date)'
                ' VALUES (?, ?, ?, ?)',
                (amount, currency, description, purchases_date)
            )
            db.commit()

            shop_order_id = db.execute(
                'select id from purchases where purchases_date = ?',
                [purchases_date]
            ).fetchall()[0]["id"]

            desc = description.replace("\n", " ")
            desc = desc.replace("\r", " ")
            current_app.logger.info(
                'POST index.html (Amount: {}, Currency: {}, Description: "{}", Id: {})'.format(
                    int(amount * 100), currency, desc, shop_order_id
                )
            )

            if currency == "EUR":  # Pay
                sign = create_sign(amount, currencies[currency], SHOP_ID, shop_order_id)
                # sign = create_sign(amount, currencies[currency], payway, SHOP_ID, shop_order_id)
                url = "https://pay.piastrix.com/ru/pay"
                method = "POST"

                values = {
                    "amount": amount,
                    "currency": currencies[currency],
                    "shop_id": SHOP_ID,
                    "sign": sign,
                    "description": description,
                    "shop_order_id": shop_order_id
                }

                return render_template('form.html', url=url, method=method, values=values)

            elif currency == "USD":  # Bill
                sign = create_sign(currencies[currency], amount, currencies[currency], SHOP_ID, shop_order_id)
                data = {
                    "payer_currency": currencies[currency],
                    "shop_amount": amount,
                    "shop_currency": currencies[currency],
                    "shop_id": SHOP_ID,
                    "shop_order_id": shop_order_id,
                    "sign": sign,
                    "description": description,
                }

                res = send_json(data)

                if res["error_code"] == 0:
                    url = res["data"]["url"]
                    return redirect(url)
                else:
                    current_app.logger.warning('Error in Bill: {}'.format(res))
                    return redirect(url_for("main.fail"))

            else:
                sign = create_sign(amount, currencies[currency], PAY_WAY, SHOP_ID, shop_order_id)
                data = {
                    "amount": amount,
                    "currency": currencies[currency],
                    "payway": PAY_WAY,
                    "shop_id": SHOP_ID,
                    "sign": sign,
                    "description": description,
                    "shop_order_id": shop_order_id
                }

                res = send_json(data, invoice=True)

                if res["error_code"] == 0:
                    url = res["data"]["url"]
                    method = res["data"]["method"]

                    values = {
                        "lang": res["data"]["data"]["lang"],
                        "m_curorderid": res["data"]["data"]["m_curorderid"],
                        "m_historyid": res["data"]["data"]["m_historyid"],
                        "m_historytm": res["data"]["data"]["m_historytm"],
                        "referer": res["data"]["data"]["referer"],
                    }

                    return render_template('form.html', url=url, method=method, values=values)
                else:
                    current_app.logger.warning('Error in Bill: {}'.format(res))
                    return redirect(url_for("main.fail"))
    else:
        return render_template('index.html')


@bp.route('/database')
def database():
    db = get_db()
    purchases = db.execute(
        'SELECT id, amount, currency, description, purchases_date'
        ' FROM purchases'
        ' ORDER BY id DESC'
    ).fetchall()

    return render_template('database.html', purchases=purchases)


@bp.route('/logs')
def logs():
    logs = deque()

    f = open("app.log", "r")
    for line in f:
        logs.appendleft(line)

    return render_template('logs.html', logs=logs)


@bp.route('/success')
def success():
    current_app.logger.info('success')
    return "success"


@bp.route('/fail')
def fail():
    current_app.logger.info('fail')
    return "fail"
