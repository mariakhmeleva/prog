from flask import Flask, jsonify, request

app = Flask(__name__)

RATES = {
    "USD": 75.50,
    "EUR": 85.25
}

@app.route('/rate')
def get_rate():
    currency = request.args.get('currency', '').upper()
    
    if currency not in RATES:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400
    
    return jsonify({"rate": RATES[currency]}), 200

if __name__ == '__main__':
    app.run(port=5000)