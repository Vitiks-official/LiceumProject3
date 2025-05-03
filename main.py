from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, abort, request, make_response, jsonify, session
from flask_mail import Mail, Message
from flask_restful import Api

from data.User import User
from data.Product import Product
from data.Gender import Gender
from data.Goal import Goal
import data.db_session as db_session

from data.UserResource import UserResource, UserListResource
from data.ProductResource import ProductResource, ProductListResource

from forms.LoginForm import LoginForm
from forms.RegisterForm import RegisterForm
from forms.VerificationForm import VerificationForm

import requests
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "vital_stats934"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "stullstul7@gmail.com"
app.config["MAIL_PASSWORD"] = "kxjg eevp rzgc ufuv"
app.config["MAIL_DEFAULT_SENDER"] = "stullstul7@gmail.com"

mail = Mail(app)

api = Api(app)
api.add_resource(UserListResource, "/api/user")
api.add_resource(UserResource, "/api/user/<int:user_id>")
api.add_resource(ProductListResource, "/api/product")
api.add_resource(ProductResource, "/api/product/<int:product_id>")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/calorie_tracker.db")

    db_sess = db_session.create_session()
    if not db_sess.query(Gender).first():
        genders = [
            Gender(gender="Мужской"),
            Gender(gender="Женский")
        ]
        db_sess.add_all(genders)
        db_sess.commit()

    if not db_sess.query(Goal).first():
        goals = [
            Goal(goal="Сбросить вес", coefficient=0.9),
            Goal(goal="Поддерживать вес", coefficient=1),
            Goal(goal="Набрать вес", coefficient=1.1)
        ]
        db_sess.add_all(goals)
        db_sess.commit()

    app.run()


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return f"hi {current_user.name} ^w^"
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    message = None
    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email).first()
        if not user:
            message = "Аккаунта с указанной почтой не существует!"
        elif not user.check_password(password):
            message = "Неверный пароль!"
        else:
            login_user(user)
            return redirect("/")

    return render_template("login.html", form=form, message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    message = None
    if form.validate_on_submit() and "verification_sent" not in session:

        email = form.email.data
        password = form.password.data
        name = form.name.data
        surname = form.surname.data
        age = form.age.data
        gender = ["Мужской", "Женский"].index(form.gender.data) + 1
        height = form.height.data
        weight = form.weight.data

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email).first()
        if user:
            message = "Аккаунт с указанной почтой уже существует!"
        elif len(password) < 8:
            message = "Пароль должен содержать не менее 8 символов!"
        elif not (any(char.isdigit() for char in password) and any(char.isalpha() for char in password)):
            message = "Пароль должен содержать и буквы, и цифры!"
        elif not (name.isalpha() and surname.isalpha()):
            message = "Имя и фамилия должны состоять из букв!"
        elif not 1 <= age <= 200:
            message = "Возраст - число от 1 до 200!"
        elif not 50 <= height <= 300:
            message = "Рост - число от 50 до 300!"
        elif not 10 <= weight <= 600:
            message = "Вес - число от 10 до 600!"
        else:
            session["registration_data"] = {
                "email": form.email.data,
                "password": password,
                "name": name,
                "surname": surname,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight
            }
            verification_code = random.randint(100000, 999999)
            session["verification_code"] = verification_code
            send_verification_email(email, verification_code)
            session["verification_sent"] = True
            return redirect("/verify_email")

    elif "verification_sent" in session:
        return redirect("/verify_email")

    return render_template("register.html", form=form, message=message)


@app.route("/verify_email", methods=["GET", "POST"])
def verify_email():
    if "verification_sent" not in session or "registration_data" not in session:
        return redirect("/register")

    form = VerificationForm()
    message = None

    if request.method == "POST":
        entered_code = form.verification_code.data
        stored_code = session.get("verification_code")
        registration_data = session.get("registration_data")

        if entered_code == stored_code and registration_data:
            post_json = requests.post(f"{request.url_root}api/user", json=session["registration_data"]).json()
            user_id = post_json["id"]

            db_sess = db_session.create_session()
            user = db_sess.query(User).get(user_id)
            login_user(user)

            session.pop("registration_data", None)
            session.pop("verification_code", None)
            session.pop("verification_sent", None)

            return redirect("/")
        else:
            message = "Неверный код подтверждения!"

    return render_template("verify_email.html", form=form, email=session["registration_data"]["email"], message=message)


@app.route("/cancel_verification")
def cancel_verification():
    session.pop("registration_data", None)
    session.pop("verification_code", None)
    session.pop("verification_sent", None)
    return redirect("/register")


def send_verification_email(email, code):
    msg = Message('Подтверждение регистрации', recipients=[email])
    msg.body = f'Ваш код подтверждения: {code}'
    mail.send(msg)


if __name__ == "__main__":
    main()
