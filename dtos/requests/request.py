from marshmallow import Schema, fields

class RequestSchema(Schema):
    ticket_id = fields.Str(data_key="ticketId")
    license_plate = fields.Str(required=True, data_key="licensePlate")
    message = fields.Str(required=True)

request_schema = RequestSchema()
