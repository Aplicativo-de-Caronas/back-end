from flask import Flask, request, url_for, redirect, make_response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
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

    def __int__(self, email, password):
        self.email = email
        self.password = password


class Profile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    celular = db.Column(db.String(20), nullable=True)

    def __init__(self, username, name, email, celular):
        self.username = username
        self.name = name
        self.email = email
        self.celular = celular


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
                # todo: tratar quando montar a criptografia
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
                # todo: tratar quando montar a criptografia
                if request.json['oldPassword'] != conta.password:
                    return make_response({"Status": "Old password wrong"}, 406)
                mudanca = []
                if 'email' in request.json:
                    conta.email = request.json['email']
                    mudanca.append('email')
                if 'password' in request.json:
                    conta.password = request.json['password']
                    mudanca.append('password')
                db.session.commit()
                if mudanca:
                    return make_response({"Status": f"{' '.join(mudanca)} changed"}, 200)
                else:
                    raise KeyError
        except KeyError:
            return make_response(
                {"Status": "Bad request",
                 "Expected": ['email', 'password', 'oldPassword'],
                 "Details": "(email or password) and oldPassword",
                 "Received": list(request.json.keys())},
                400)
        except IntegrityError:
            return make_response({"Status": "Email already exists"}, 409)

    elif request.method == "DELETE":
        session.clear()
        return make_response({"Status": f"Nada mudou"}, 200)


@app.route("/login", methods=["POST", "DELETE"])
def login():
    if request.method == "POST":
        pass  # todo: login
    elif request.method == "DELETE":
        pass  # todo: logout


@app.route("/users", methods=["GET", "POST", "PUT", "DELETE"])
def Usuario():
    if request.method == "GET":
        users = db.session.execute(db.select(Profile).order_by(Profile.username)).scalars()
        return make_response(users)
    elif request.method == "POST":
        usr = Profile(
            username=request.form['username'],
            name=request.form['name'],
            email=request.form['email'],
            celular=request.form['celular']
        )
        db.session.add(usr)
        db.commit()
    elif request.method == "PUT":
        passG
    elif request.method == "DELETE":
        pass
    return make_response()


@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return make_response({"Valid": True})


@app.route("/user/<int:id>")
def user_detail(id_detail):
    usera = db.get_or_404(Profile, id_detail)
    return make_response(usera)


@app.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id_delete):
    user = db.get_or_404(Profile, id_delete)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    return make_response(user)


@app.route("/teste/<name>")
def user_de(name):
    session.permanent = True
    session['user'] = name
    return "Hi!"


@app.route("/teste")
def user():
    if "user" in session:
        return session['user']
    else:
        return "Error"


if __name__ == "__main__":
    app.run(host="localhost", port=8590, debug=True)
