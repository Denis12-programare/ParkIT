from database import db

class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)
    entry_station = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
