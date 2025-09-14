from models.intent import Intent
from database import db

class IntentsService:
    def create(self, name: str, description: str):
        payment = Intent(name=name, description=description)

        db.session.add(payment)
        db.session.commit()

        return payment