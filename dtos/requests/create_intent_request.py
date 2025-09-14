from marshmallow import Schema, fields

class CreateIntentRequestSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)

create_intent_request_schema = CreateIntentRequestSchema()