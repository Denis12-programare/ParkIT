from sqlite3.dbapi2 import connect
from flask import Flask, make_response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
import requests
import sqlite3
from models.payment import Payment
from models.intent import Intent
from database import db
from dtos.requests.request import request_schema
from dtos.requests.create_intent_request import create_intent_request_schema
from marshmallow import ValidationError

from services.intents_service import IntentsService

app = Flask(__name__)

app.config.from_object(Config);

db.init_app(app)

intents_service = IntentsService()

@app.route('/api/v1/operator/handle', methods=['POST'])
def index():
    try:
        data = request_schema.load(request.get_json())
    except ValidationError as error:
        return jsonify(error.messages), 400

    req = {
        "intent": "generated_intent"
        "ticket_id": data["ticket_id"],
        "license_plate": data["license_plate"]
    }
    print(data)

    return "Succes"

@app.route("/api/v1/intents", methods=['POST'])
def create():
    try:
        data = create_intent_request_schema.load(request.get_json())
    except ValidationError as error:
        return jsonify(error.messages), 400

    intent = intents_service.create(data["name"], data["description"])

    result = {
        "id": intent.id,
        "name": intent.name,
        "description": intent.description
    }

    return jsonify(result), 200

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
