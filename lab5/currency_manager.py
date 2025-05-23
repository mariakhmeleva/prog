from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="currency_db", user="postgres", password="postgres", host="localhost", port="5432")
cur = conn.cursor()


@app.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    name, rate = data['currency_name'], data['rate']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if cur.fetchone():
        return jsonify({"error": "Данная валюта уже существует"}), 400
    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
    conn.commit()
    return jsonify({"status": "OK"}), 200

@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    name, rate = data['currency_name'], data['rate']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if not cur.fetchone():
        return jsonify({"error": "Валюта не найдена"}), 404
    cur.execute("UPDATE currencies SET rate=%s WHERE currency_name=%s", (rate, name))
    conn.commit()
    return jsonify({"status": "OK"}), 200

@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    name = data['currency_name']
    cur.execute("SELECT * FROM currencies WHERE currency_name=%s", (name,))
    if not cur.fetchone():
        return jsonify({"error": "Валюта не найдена"}), 404
    cur.execute("DELETE FROM currencies WHERE currency_name=%s", (name,))
    conn.commit()
    return jsonify({"status": "OK"}), 200


@app.route('/set_role', methods=['POST'])
def set_role():
    data = request.json
    telegram_id = data['telegram_id']
    role = data['role']
    if role not in ['admin', 'user']:
        return jsonify({"error": "Invalid role"}), 400
    cur.execute("SELECT * FROM users WHERE telegram_id=%s", (telegram_id,))
    if cur.fetchone():
        cur.execute("UPDATE users SET role=%s WHERE telegram_id=%s", (role, telegram_id))
    else:
        cur.execute("INSERT INTO users (telegram_id, role) VALUES (%s, %s)", (telegram_id, role))
    conn.commit()
    return jsonify({"status": "role updated"}), 200

# Получить роль
@app.route('/get_role/<int:telegram_id>', methods=['GET'])
def get_role(telegram_id):
    cur.execute("SELECT role FROM users WHERE telegram_id=%s", (telegram_id,))
    row = cur.fetchone()
    if row:
        return jsonify({"role": row[0]}), 200
    return jsonify({"role": "user"}), 200 


if __name__ == '__main__':
    app.run(port=5001)
