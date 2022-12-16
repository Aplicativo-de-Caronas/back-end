from flask import Flask, request, url_for, redirect, make_response, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
# Configurador DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app_caronas.sqlite3"
db = SQLAlchemy(app)

# Configurador Session
app.secret_key = 'oaskdfoakfoak'
app.permanent_session_lifetime = timedelta(days=15)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    celular = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return make_response(make_json(users, default_all=False, avoid=["email", "username"]))
@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return make_response({"Valid": True})


@app.route("/user/<int:id>")
def user_detail(id_detail):
    user = db.get_or_404(User, id_detail)
    return make_response(user)


@app.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id_delete):
    user = db.get_or_404(User, id_delete)

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
    app.debug = True
    app.run()
