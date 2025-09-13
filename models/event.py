from database import db

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, nullable=False)
    station_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False)
    payload_json = db.Column(db.String, nullable=False)
    