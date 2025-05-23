from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="currency_db", user="postgres", password="postgres", host="localhost", port="5432")
cur = conn.cursor()

@app.route('/convert', methods=['GET'])
def convert():
    currency = request.args.get('currency_name')
    amount = float(request.args.get('amount'))
    cur.execute("SELECT rate FROM currencies WHERE currency_name=%s", (currency,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "Валюта не найдена"}), 404
    rub_amount = amount * float(row[0])
    return jsonify({"converted": rub_amount}), 200

@app.route('/currencies', methods=['GET'])
def currencies():
    cur.execute("SELECT currency_name, rate FROM currencies")
    rows = cur.fetchall()
    return jsonify([{"currency_name": r[0], "rate": float(r[1])} for r in rows]), 200

if __name__ == '__main__':
    app.run(port=5002)
