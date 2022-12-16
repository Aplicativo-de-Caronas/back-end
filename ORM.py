class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    celular = db.Column(db.String, nullable=False)

class Agenda(db.Model):
    id = db.Column(db.UUID) # Ver UUID
    dia = db.Column(db.Date)
    ida = db.Column(db.Binary)
    hora = db.Column(db.Integer)

class Profile(db.Model):
    id = db.Column(db)