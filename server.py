from flask import Flask, make_response, redirect, render_template, request, session
import requests
import sqlite3
import uuid
from datetime import datetime
#import cv2
#import easyocr
#import numpy as np
#from ultralytics import YOLO

STATION_ID=1
conn = sqlite3.connect('Parking.db')
cursor = conn.cursor()
cursor.execute('SELECT kind FROM station WHERE id=?', (STATION_ID,))
station_type = cursor.fetchone()[0]
cursor.close()
conn.close()

TEMPLATE = """
User payment status: {}

Rules for classification:
{}

User's issue:
{}
"""

#reader = easyocr.Reader(['en'], gpu=False)
#yolo_model = YOLO("license_plate_detector.pt")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'HPcuCxupfxbQEXauwkMM'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    print(f'user confirmed {session['vrn_confirm']}')
    return make_response({}, 200)

@app.route('/pay', methods=['GET'])
def pay():
    input = request.args.get('token')
    if input is None:
        return redirect('/')
    # extract "invoice" based on token and render it
    return render_template('pay.html')

@app.route('/upload', methods=['POST'])
def upload():

    if "image" not in request.files:
        return "No image received", 400

    file = request.files["image"]
    file_bytes = np.frombuffer(file.read(), np.uint8)

    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    results = yolo_model(img)

    plates = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = img[y1:y2, x1:x2]

            ocr_results = reader.readtext(crop)
            for (_, text, conf) in ocr_results:
                if conf > 0.9:
                    plates.append(text.strip())
    session['vrn_confirm'] = '_'.join(plates)
    return make_response({'plate': session['vrn_confirm'] if len(plates) else None}, 200)

@app.route('/qr', methods=['GET'])
def qr():
    return render_template('test.html')

@app.route('/get_intent', methods=['POST'])
def intent():
    data = request.json
    if data == None:
        return make_response({'status': 'bad request'}, 400)
    conn = sqlite3.connect('Parking.db')
    cursor = conn.cursor()
    intents = cursor.execute('SELECT * from intents').fetchall()
    rules = ''
    for intent in intents:
        rules += intent[1] + ' -> ' + intent[2] + '\n'

    #TO IMPLEMENT
    #query license plate/ticket and get payment status

    resp = requests.post('http://127.0.0.1:11434/api/generate', json={'model': 'parking_assistant2', 'prompt': TEMPLATE.format('<null>', rules, data['input']), 'stream': False})
    resp = resp.json()['response'].strip()
    #resp = 'no_payment_confirmation'
    return make_response({'intent': resp}, 200)

@app.route('/decision', methods=['POST'])
def decision():
    data = request.json
    return_data = {}
    if data == None:
        return make_response({'status': 'bad request'}, 400)
    conn = sqlite3.connect('Parking.db')
    cursor = conn.cursor()
    resp = data['intent']
    entry_time = data['entry_time'] if resp == 'ticket_lost' or resp == 'no_payment_confirmation' else ''
    match resp:
        case 'ticket_lost':
            if station_type == 'exit_terminal':
                return make_response({'tts_invokation': 'cant print the ticket. Please free the lane and go to another terminal'}, 200) 
            ticket_id = cursor.execute('SELECT ticket_id from session where entry_time=?', (entry_time,)).fetchone()[0]
            new_ticket = str(uuid.uuid4())
            print(f'Your new ticket is {new_ticket}')
            conn.execute('UPDATE ticket set status="LOST" where id=? and status <> LOST',(ticket_id,))
            #issued_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute('INSERT INTO ticket (code, issued_at, entry_station, status) values (?, ?, ?, ?)', (new_ticket, entry_time, STATION_ID, 'ACTIVE'))
            conn.commit()
            return_data['new_ticket'] = new_ticket
        case 'no_payment_confirmation':
            ticket_code = data['ticket_code']
            db_entry_time = cursor.execute('select entry_time from session join ticket on session.ticket_id=ticket.id where code=?', (ticket_code,)).fetchone()[0]
            print(db_entry_time)
            if db_entry_time != entry_time:
                return make_response({'status': 'check entry time/VRN one more time because we didnt find your record in our database'}, 400)
            events = cursor.execute('select type from event join session on session.id=event.session_id join ticket on session.ticket_id=ticket.id where session.entry_time=? and ticket.code=?', (entry_time, ticket_code)).fetchall()
            for event in events:
                if 'PAYMENT_OK' == event[0]:
                    # implement event log
                    return make_response({'tts_invokation': 'barrier raised'}, 200)
            return_data['context'] = 'scan_qr'
        case 'forgot_pay':
            # explains same thing that the operrator does
            # if car still stays then scanqr and open barrier
            pass
    
    tts_text = cursor.execute('SELECT action FROM intents WHERE intent = ?', (resp,)).fetchone()[0]
    return_data['tts_invokation'] = tts_text
    return make_response(return_data, 200)

@app.route('/addintent', methods=['POST'])
def addintent():
    input = request.json
    if input == None:
        return make_response({'status': 'no data'}, 400)
    conn = sqlite3.connect('Parking.db')
    conn.execute('INSERT INTO intents (intent, description, action) values (?, ?, ?)', (input['intent'], input['description'], input['action']))
    conn.commit()
    return make_response({}, 200)

app.run(host='0.0.0.0', port=8000)
