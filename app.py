from flask import Flask, request, make_response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from erros import *
from validators import Validator
import uuid

app = Flask(__name__)
# Configurador DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://app:app-caronas@localhost:5432/appcaronas'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configurador Session
app.secret_key = 'oaskdfoakfoak'
app.permanent_session_lifetime = timedelta(days=15)


class Account(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    profile = db.relationship('Profile', backref='profile', cascade="all, delete-orphan")

    def __int__(self, email, password):
        self.email = email
        self.password = password


class Profile(db.Model):
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey("account.id"), primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    celular = db.Column(db.String(20), nullable=True)
    cpf = db.Column(db.String(15), nullable=True)

    def __init__(self, firstName, lastName, celular,cpf, account):
        self.firstName = firstName
        self.lastName = lastName
        self.celular = celular
        self.cpf = cpf
        self.account_id = account


with app.app_context():
    db.create_all()


@app.route("/account", methods=["POST", "PUT", "DELETE"])
def Conta():
    session.permanent = True
    if request.method == "POST":
        try:
            if 'account_id' in session:
                return make_response({"Status": "Account is logged"}, 406)
            else:
                # todo: criptografia e requisitos
                conta = Account(
                    password=request.json['password'],
                    email=request.json['email']
                )
                db.session.add(conta)
                db.session.commit()
                session['account_id'] = conta.id
                return make_response({"Status": "Success"}, 200)
        except KeyError:
            return make_response({"Status": "Bad request",
                                  "Expected": ['email', 'password'],
                                  "Received": list(request.json.keys())}, 400)
        except IntegrityError:
            return make_response({"Status": "Email already exists"}, 409)

    elif request.method == "PUT":
        try:
            if 'account_id' not in session:
                return make_response({"Status": "Not Logged"}, 401)
            else:
                conta = Account.query.filter_by(id=session['account_id']).first()
                # todo: criptografia
                if request.json['actualPassword'] != conta.password:
                    return make_response({"Status": "Actual password wrong"}, 406)

                mudanca = request.json['change']
                if not {"password", "email"}.issuperset(mudanca) or not mudanca:
                    return make_response(
                        {"Status": "Bad request",
                         "Expected": ['email', 'newPassword'],
                         "Details": "Expect only the 2 aboves itens in change",
                         "Received": mudanca},
                        400)
                else:
                    for item in mudanca:
                        exec(f"conta.{item} = request.json['{item}']")
                    db.session.commit()
                    if mudanca:
                        return make_response({"Status": f"{' '.join(mudanca)} changed"}, 200)
                    else:
                        raise KeyError
        except KeyError:
            return make_response(
                {"Status": "Bad request",
                 "Expected": ['email', 'password', 'actualPassword', "change"],
                 "Details": "changed is what you gonna change, email or password accepted,"
                            "and only need the specified field",
                 "Received": list(request.json.keys())},
                400)
        except IntegrityError:
            return make_response({"Status": "Email already exists"}, 409)

    elif request.method == "DELETE":
        # todo: criptografia
        if 'account_id' not in session:
            return make_response({"Status": "Unauthorized, make login first"}, 401)
        else:
            conta = Account.query.filter_by(id=session['account_id'],
                                            password=request.json['password']).first()
            if conta:
                db.session.delete(conta)
                db.session.commit()
                session.clear()
                return make_response({"Status": "Success"}, 202)
            else:
                return make_response({"Status": "Wrong Password"}, 404)

# todo: recuperar senha
@app.route("/login", methods=["GET", "POST", "DELETE"])
def login():
    if request.method == "POST":
        try:
            # todo: criptografia
            conta = Account.query.filter_by(email=request.json['email'], password=request.json['password']).first()
            if "account_id" in session:
                return make_response({"Status": f"Already logged"}, 418)
            if conta:
                session.permanent = True
                session['account_id'] = conta.id
                return make_response({"Status": f"Success"}, 200)
            else:
                return make_response({"Status": f"Not Found"}, 404)
        except KeyError:
            return make_response(
                {"Status": "Bad request",
                 "Expected": ['email', 'password'],
                 "Received": list(request.json.keys())},
                400)
    elif request.method == "DELETE":
        if "account_id" in session:
            session.clear()
            return make_response({"Status": f"Logout"}, 202)
        else:
            return make_response({"Status": f"already logout"}, 401)
    elif request.method == "GET":
        if "account_id" in session:
            return make_response({"Status": f"logged", "Account_ID": session["account_id"]}, 200)
        else:
            return make_response({"Status": f"Not Logged"}, 401)


@app.route("/profile", methods=["GET", "POST", "PUT", "DELETE"])
def Usuario():
    if request.method == "GET":
        if 'account_id' not in session:
            return make_response({"Status": f"Unauthorized"}, 401)
        else:
            profile = Profile.query.filter_by(account_id=session['account_id']).first()
            if profile:
                return make_response({"firstName": profile.firstName,
                                      "lastName": profile.lastName,
                                      "cellphone": profile.celular,
                                      "cpf": f"{profile.cpf[0:3]}.***.***-{profile.cpf[9:-1]}"}, 200)
            else:
                return make_response({"Status": f"Not Found"}, 404)
    elif request.method == "POST":
        try:
            Validator.cpf(request.json['cpf'])
            prof = Profile(
                firstName=request.json['firstName'],
                lastName=request.json['lastName'],
                celular=request.json['cellphone'],
                cpf=request.json['cpf'],
                account=Account.query.filter_by(id=session['account_id']).first().id
            )
            db.session.add(prof)
            db.session.commit()
            return make_response({"Status": f"Success"}, 200)
        except KeyError:
            return make_response(
                {"Status": "Bad request",
                 "Expected": ['firstName', 'lastName', 'cellphone', 'cpf'],
                 "Received": list(request.json.keys())},
                400)
        except IntegrityError:
            return make_response({"Status": "Already has a profile"}, 409)
        except InvalidCpf:
            return make_response({"Status": "Invalid CPF"}, 406)
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        pass
    return make_response()


if __name__ == "__main__":
    app.run(host="localhost", port=8590, debug=True)
