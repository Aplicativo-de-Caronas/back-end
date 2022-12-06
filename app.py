from flask import Flask, request, url_for, redirect, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app_caronas.sqlite3"
db = SQLAlchemy(app)


def make_json(clss, default_all=True, avoid=None):
    if avoid is None:
        avoid = set()

    if default_all:
        avoid.add("_sa_instance_state")
        selects = set()
        output = []
        for item in clss:
            temp = {}
            if not selects:
                selects = set(item.__dict__.keys()) - avoid
            for select in selects:
                temp.update({select: item.__dict__[select]})
            output.append(temp)
        return output
    else:
        selects = set(avoid)
        output = []
        for item in clss:
            temp = {}
            for select in selects:
                temp.update({select: item.__dict__[select]})
            output.append(temp)
        return output


class students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))
    pin = db.Column(db.String(10))

    def __init__(self, name, city, addr, pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)


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


if __name__ == "__main__":
    app.run()
