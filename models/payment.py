from database import db

class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, nullable=False)
    station_id = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String, nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)