from database import db

class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    entry_station = db.Column(db.Integer, nullable=False)
    exit_time = db.Column(db.DataTime, nullable=False)
    exit_station = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    amount_due_cents = db.Column(db.Decimal, nullable=False)
    amount_paid_cents = db.Column(db.Decimal, nullable=False)
    paid_until = db.Column(db.DateTime, nullable=False)
    license_plate_entry = db.Column(db.String, nullable=False)
    license_plate_exit = db.Column(db.String, nullable=False)