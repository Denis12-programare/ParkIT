from sqlite3.dbapi2 import connect
from flask import Flask, make_response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
import requests
import sqlite3
from models.payment import Payment
from database import db

TEMPLATE = """
User payment status: {}

Rules for classification:
{}

User's issue:
{}
"""
#rules = """
#- ticket_lost → The user lost their entry ticket.
#- forgot_pay → The user forgot to pay before reaching the exit. (They may mention forgetting, not realizing they had to pay, or say they don't know what to do.)
#- not_paid → Only if the user explicitly mentions they already tried to pay (payment attempted, payment failed, card declined, machine error, barrier did not open after trying to pay).
#"""

app = Flask(__name__)

app.config.from_object(Config);

db.init_app(app)

@app.route('/payments', methods=['GET'])
def findAll():
    with app.app_context():
        payments = Payment.query.all()
    
    payments_list = [
        {
            'id': p.id,
            'session_id': p.session_id,
            'station_id': p.station_id,
            'method': p.method,
            'amount_cents': p.amount_cents,
            'approved': p.approved,
            'created_at': p.created_at.isoformat()
        } for p in payments
    ]
    
    return jsonify(payments_list)

@app.route('/decision', methods=['POST'])
def decision():
    data = request.json
    if data == None:
        return make_response({'status': 'bad request'}, 400)
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    intents = cursor.execute('SELECT * from intents').fetchall()
    rules = ''
    for intent in intents:
        rules += intent[1] + ' -> ' + intent[2] + '\n'

    resp = requests.post('http://127.0.0.1:11434/api/generate', json={'model': 'parking_assistant', 'prompt': TEMPLATE.format('no_payment', rules, data['input']), 'stream': False})
    resp = resp.json()['response'].strip()

    return make_response({'resp': resp}, 200)

@app.route('/addintent', methods=['POST'])
def addintent():
    input = request.json
    if input == None:
        return make_response({'status': 'no data'}, 400)
    conn = sqlite3.connect('test.db')
    conn.execute('INSERT INTO intents (intent, description, action) values (?, ?, ?)', (input['intent'], input['description'], input['action']))
    conn.commit()
    return make_response({}, 200)

app.run(host='0.0.0.0', port=8000)
