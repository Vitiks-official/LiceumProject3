from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, abort, request, make_response, jsonify, session, url_for
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
from forms.EditProfileForm import EditProfileForm

import requests
import random
import os

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
    if not current_user.is_authenticated:
        return redirect("/login")

    return render_template("index.html", avatar_url=get_avatar_url())


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
        gender = form.gender.data
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
        elif not 5 <= age <= 200:
            message = "Возраст - число от 5 до 200!"
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


@login_required
@app.route("/profile", methods=["GET", "POST"])
def profile_settings():
    form = EditProfileForm(obj=current_user)
    imt = round(current_user.weight / (current_user.height / 100) ** 2, 1)
    if imt < 16:
        result = "Значительный дефицит"
    elif 16 <= imt < 18.5:
        result = "Дефицит"
    elif 18.5 <= imt <= 25:
        result = "Норма"
    elif 25 < imt < 30:
        result = "Лишний вес"
    elif 30 <= imt < 35:
        result = "Ожирение I"
    elif 35 <= imt <= 40:
        result = "Ожирение II"
    else:
        result = "Ожирение III"

    if form.validate_on_submit():
        avatar_file = form.avatar.data
        if avatar_file:
            avatar_file.save(f"static/img/avatar/user_{current_user.id}.png")

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)

        user.goal = form.goal.data
        user.height = form.height.data
        user.weight = form.weight.data
        user.age = form.age.data

        db_sess.commit()
        return redirect("/profile")

    return render_template("profile.html", form=form, avatar_url=get_avatar_url(), imt=imt, result=result)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@login_required
@app.route("/delete")
def delete():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.delete(user)
    db_sess.commit()
    try:
        os.remove(f"static/img/avatar/user_{current_user.id}.png")
    except Exception as error:
        print(error)
    return redirect("/")


def send_verification_email(email, code):
    msg = Message("Подтверждение регистрации", recipients=[email])
    msg.body = f"Ваш код подтверждения: {code}"
    mail.send(msg)


def get_avatar_url():
    path = f"img/avatar/user_{current_user.id}.png"
    if os.path.exists("static/" + path):
        return url_for("static", filename=path)
    return url_for("static", filename="img/avatar/default.png")


if __name__ == "__main__":
    main()
