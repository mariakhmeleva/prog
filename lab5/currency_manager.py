from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="currency_db", user="postgres", password="postgres", host="localhost", port="5432")
cur = conn.cursor()

# Создание таблицы при первом запуске


@app.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    name, rate = data['currency_name'], data['rate']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if cur.fetchone():
        return jsonify({"error": "Currency already exists"}), 400
    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
    conn.commit()
    return jsonify({"status": "OK"}), 200

@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    name, rate = data['currency_name'], data['rate']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if not cur.fetchone():
        return jsonify({"error": "Currency not found"}), 404
    cur.execute("UPDATE currencies SET rate=%s WHERE currency_name=%s", (rate, name))
    conn.commit()
    return jsonify({"status": "OK"}), 200

@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    name = data['currency_name']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if not cur.fetchone():
        return jsonify({"error": "Currency not found"}), 404
    cur.execute("DELETE FROM currencies WHERE currency_name=%s", (name,))
    conn.commit()
    return jsonify({"status": "OK"}), 200

if __name__ == '__main__':
    app.run(port=5001)
