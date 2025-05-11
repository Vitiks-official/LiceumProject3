from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, request, session, url_for
from flask_mail import Mail, Message
from flask_restful import Api

from data.User import User
from data.Product import Product
from data.Statistics import Statistics
from data.Lifestyle import Lifestyle
from data.Article import Article
from data.Gender import Gender
from data.Goal import Goal
from sqlalchemy import or_, and_
import data.db_session as db_session

from data.UserResource import UserResource, UserListResource
from data.ProductResource import ProductResource, ProductListResource
from data.ArticleResource import ArticleResource

from forms.LoginForm import LoginForm
from forms.RegisterForm import RegisterForm
from forms.VerificationForm import VerificationForm
from forms.EditProfileForm import EditProfileForm
from forms.AddArticleForm import AddArticleForm
from forms.AddProductForm import AddProductForm

from bot.admin_bot import send_product_request_to_admin, send_article_request_to_admin

import requests
import datetime
import decimal
import asyncio
import random
import json
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
api.add_resource(ArticleResource, "/api/article/<int:article_id>")

login_manager = LoginManager()
login_manager.init_app(app)


# User loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Main function, adding data to database, launching the application
def main():
    db_session.global_init("db/calorie_tracker.db")

    db_sess = db_session.create_session()
    if not db_sess.query(Gender).first():
        genders = [
            Gender(gender="Мужской"),
            Gender(gender="Женский")
        ]
        db_sess.add_all(genders)

    if not db_sess.query(Goal).first():
        goals = [
            Goal(goal="Сбросить вес", addition=-500),
            Goal(goal="Поддерживать вес", addition=0),
            Goal(goal="Набрать вес", addition=500)
        ]
        db_sess.add_all(goals)

    if not db_sess.query(Lifestyle).first():
        lifestyles = [
            Lifestyle(lifestyle="Сидячий образ жизни", coefficient=1.2),
            Lifestyle(lifestyle="Низкая активность", coefficient=1.375),
            Lifestyle(lifestyle="Умеренная активность", coefficient=1.55),
            Lifestyle(lifestyle="Высокая активность", coefficient=1.725),
            Lifestyle(lifestyle="Очень высокая активность", coefficient=1.9)
        ]
        db_sess.add_all(lifestyles)

    if not db_sess.query(Product).first():
        with open("static/json/products.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for product in data:
            proteins, fats, carbohydrates = list(map(float, product["bgu"].split(",")))
            db_sess.add(Product(name=product["name"].lower(),
                                calories=int(float(product["kcal"])),
                                proteins=round(proteins, 1),
                                fats=round(fats, 1),
                                carbohydrates=round(carbohydrates, 1)))

    if not db_sess.query(Article).first():
        articles_content = list()
        for i in range(3):
            with open(f"static/txt/article_{i + 1}.txt", "r", encoding="utf-8") as file:
                articles_content.append(file.read())

        articles = [
            Article(title="Основы здорового питания: баланс и разнообразие",
                    content=articles_content[0]),
            Article(title="Ключ к контролю веса: понимание калорий",
                    content=articles_content[1]),
            Article(title="Вода – незаменимый элемент здорового питания",
                    content=articles_content[2])
        ]
        db_sess.add_all(articles)

    db_sess.commit()
    app.run()


# Index page of the app
@app.route("/")
@app.route("/index")
def index():
    if not current_user.is_authenticated:
        return redirect("/login")

    db_sess = db_session.create_session()

    stat = db_sess.query(Statistics).filter(Statistics.user == current_user.id,
                                            Statistics.date == datetime.date.today()).first()
    if stat:
        values = (stat.calories, stat.proteins, stat.fats, stat.carbohydrates)
        progress = [round(value / norm * 100) for value, norm in zip(values, get_norms())]
        progress = [100 if x > 100 else x for x in progress]

        all_pfc = stat.proteins + stat.fats + stat.carbohydrates
        ratios = [str(round(x / all_pfc * 100)) for x in (stat.proteins, stat.fats, stat.carbohydrates)]

        pairs = [f"{value}/{norm}" for value, norm in zip(values, get_norms())]
    else:
        progress = [0] * 4
        ratios = ["33", "33", "33"]
        pairs = [f"0/{norm}" for norm in get_norms()]

    articles = db_sess.query(Article).all()

    return render_template("index.html", avatar_url=get_avatar_url(), progress=progress, ratios=ratios, pairs=pairs,
                           articles=articles)


# Page for logging the user in
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


# Page for user registration
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
            print(verification_code)
            session["verification_code"] = verification_code
            send_verification_email(email, verification_code)
            session["verification_sent"] = True
            return redirect("/verify_email")

    elif "verification_sent" in session:
        return redirect("/verify_email")

    return render_template("register.html", form=form, message=message)


# Page for user's email verification during registration
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


# Canceling user registration
@app.route("/cancel_verification")
def cancel_verification():
    session.pop("registration_data", None)
    session.pop("verification_code", None)
    session.pop("verification_sent", None)
    return redirect("/register")


# Page for browsing and editing user's profile settings
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
        user.lifestyle = form.lifestyle.data
        user.height = form.height.data
        user.weight = form.weight.data
        user.age = form.age.data

        db_sess.commit()
        return redirect("/profile")

    return render_template("profile.html", form=form, avatar_url=get_avatar_url(), imt=imt, result=result)


# Page for adding a meal in the app
@login_required
@app.route("/add_meal")
def add_meal():
    search = request.args.get("search", "")

    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(
        Product.name.like(f"%{search.lower()}%")).filter(
        or_(and_(Product.public == True, Product.accepted == True), Product.user == current_user.id)).all()

    delete_id = request.args.get("remove_id", "")

    add_id = request.args.get("add_id", "")
    add_mass = request.args.get("add_mass", "")
    choice = request.args.get("choice", "")

    choice_dict = dict()
    if choice:
        pairs = [x.split("_") for x in choice.split("$")]
        for id_, mass in pairs:
            choice_dict[id_] = int(mass)

    if delete_id:
        choice_dict.pop(delete_id)
        new_choice = "$".join([f"{id_}_{mass}" for id_, mass in list(choice_dict.items())])

        return redirect(f"/add_meal?search={search}&choice={new_choice}")

    if add_id:
        choice_dict[add_id] = choice_dict.get(add_id, 0) + int(add_mass)
        new_choice = "$".join([f"{id_}_{mass}" for id_, mass in list(choice_dict.items())])

        return redirect(f"/add_meal?search={search}&choice={new_choice}")

    db_sess = db_session.create_session()
    added_products = list()
    total = {"calories": 0, "proteins": 0, "fats": 0, "carbohydrates": 0}
    for id_ in choice_dict:
        product = db_sess.query(Product).get(int(id_))
        mass = choice_dict[id_]

        total["calories"] += round(product.calories * mass * 0.01, 1)
        total["proteins"] += round(product.proteins * mass * 0.01, 1)
        total["fats"] += round(product.fats * mass * 0.01, 1)
        total["carbohydrates"] += round(product.carbohydrates * mass * 0.01, 1)

        added_products.append({
            "name": product.name,
            "mass": mass,
            "id": product.id
        })

    return render_template("add_meal.html", avatar_url=get_avatar_url(), search_query=search,
                           available_products=products, added_products=added_products, choice=choice, total=total)


# Page for adding a new product to the database
@login_required
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    form = AddProductForm()

    if form.validate_on_submit():
        name = form.product.data

        calories = round(form.calories.data, 1)
        proteins = round(form.proteins.data, 1)
        fats = round(form.fats.data, 1)
        carbohydrates = round(form.carbohydrates.data, 1)

        is_public = form.is_public.data

        db_sess = db_session.create_session()
        product = Product(
            name=name.lower(),
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates,
            user=current_user.id,
            public=is_public,
            accepted=current_user.is_admin
        )
        db_sess.add(product)
        db_sess.commit()

        if not current_user.is_admin and product.public:
            asyncio.run(send_product_request_to_admin(f"{request.root_url}api/product/{product.id}"))

        return redirect("/add_meal")

    elif request.method == "POST":
        return render_template("add_product.html", avatar_url=get_avatar_url(), form=form,
                               message="Неверный формат ввода величин!")

    return render_template("add_product.html", avatar_url=get_avatar_url(), form=form)


# Page for confirming added meal
@login_required
@app.route("/confirm_meal/<string:choice>")
def confirm_meal(choice):
    pairs = [[int(y) for y in x.split("_")] for x in choice.split("$")]
    calories = proteins = fats = carbohydrates = 0

    db_sess = db_session.create_session()
    for id_, mass in pairs:
        product = db_sess.query(Product).get(int(id_))
        calories += product.calories * mass * 0.01
        proteins += product.proteins * mass * 0.01
        fats += product.fats * mass * 0.01
        carbohydrates += product.carbohydrates * mass * 0.01

    calories = round(calories, 1)
    proteins = round(proteins, 1)
    fats = round(fats, 1)
    carbohydrates = round(carbohydrates, 1)

    stat = db_sess.query(Statistics).filter(Statistics.date == datetime.date.today(),
                                            Statistics.user == current_user.id).first()
    if not stat:
        stat = Statistics(
            user=current_user.id,
            date=datetime.date.today(),
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates
        )
        db_sess.add(stat)
    else:
        stat.calories += decimal.Decimal(calories)
        stat.proteins += decimal.Decimal(proteins)
        stat.fats += decimal.Decimal(fats)
        stat.carbohydrates += decimal.Decimal(carbohydrates)

    db_sess.commit()
    return redirect("/")


# Page for browsing user's statistics
@login_required
@app.route("/statistics")
def statistics():
    db_sess = db_session.create_session()
    stats = db_sess.query(Statistics).filter(Statistics.user == current_user.id).all()[-7:]

    dates = [""] + [str(x.date) for x in sorted(stats, key=lambda obj: obj.date)] + [""]

    calories_consumption = [0] + [float(x.calories) for x in stats] + [0]
    proteins_consumption = [0] + [float(x.proteins) for x in stats] + [0]
    fats_consumption = [0] + [float(x.fats) for x in stats] + [0]
    carbohydrates_consumption = [0] + [float(x.carbohydrates) for x in stats] + [0]

    return render_template("statistics.html", avatar_url=get_avatar_url(), norms=get_norms(), dates=dates,
                           calorie_data=calories_consumption, protein_data=proteins_consumption,
                           fat_data=fats_consumption, carbs_data=carbohydrates_consumption)


# Page for browsing all articles
@login_required
@app.route("/article_list")
def article_list():
    db_sess = db_session.create_session()
    articles = db_sess.query(Article).filter(Article.accepted)
    articles = zip(articles, [get_article_picture_url(x.id) for x in articles])

    return render_template("article_list.html", avatar_url=get_avatar_url(), articles=articles)


# Page for browsing an article
@login_required
@app.route("/article/<int:article_id>")
def article_browse(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not article.accepted:
        return redirect("/article_list")

    return render_template("article.html", avatar_url=get_avatar_url(), article=article,
                           picture_url=get_article_picture_url(article.id))


# Page for adding new article to the database
@login_required
@app.route("/add_article", methods=["GET", "POST"])
def add_article():
    form = AddArticleForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        article = Article(
            title=title,
            content=content,
            user=current_user.id,
            accepted=current_user.is_admin
        )

        db_sess = db_session.create_session()
        db_sess.add(article)
        db_sess.commit()

        picture = form.picture.data
        if picture:
            picture.save(f"static/img/article/article_{article.id}.png")

        if not current_user.is_admin:
            asyncio.run(send_article_request_to_admin(f"{request.root_url}api/article/{article.id}"))

        return redirect("/article_list")

    return render_template("add_article.html", avatar_url=get_avatar_url(), form=form)


# Page for logging the user out
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


# Page for deleting a user from the database
@login_required
@app.route("/delete_user")
def delete_user():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.delete(user)
    db_sess.commit()

    avatar_path = f"static/img/avatar/user_{current_user.id}.png"
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

    return redirect("/")


# Page for deleting an article from the database
@login_required
@app.route("/delete_article/<int:article_id>")
def delete_article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not (current_user.is_admin or current_user.id == article.user):
        return redirect("/article_list")

    db_sess.delete(article)
    db_sess.commit()

    pic_path = f"static/img/article/article_{article.id}.png"
    if os.path.exists(pic_path):
        os.remove(pic_path)

    return redirect("/article_list")


# Page for the authors
@app.route("/authors")
def authors():
    return render_template("authors.html", avatar_url=get_avatar_url())


# Function for sending verification email during registration
def send_verification_email(email, code):
    msg = Message("Подтверждение регистрации", recipients=[email])
    msg.body = f"Ваш код подтверждения: {code}"
    mail.send(msg)


# Function for getting user's avatar url
def get_avatar_url():
    path = f"img/avatar/user_{current_user.id}.png"
    if os.path.exists("static/" + path):
        return url_for("static", filename=path)
    return url_for("static", filename="img/avatar/default.png")


# Function for getting article picture url
def get_article_picture_url(article_id):
    path = f"img/article/article_{article_id}.png"
    if os.path.exists("static/" + path):
        return url_for("static", filename=path)
    return url_for("static", filename="img/article/default.png")


# Function for getting calories and micronutrient norms for the user
def get_norms():
    bmr = (10 * current_user.weight + 6.25 * current_user.height - 5 * current_user.age +
           (5 if current_user.gender == 1 else -161))

    db_sess = db_session.create_session()
    bmr *= db_sess.query(Lifestyle).filter(Lifestyle.id == current_user.lifestyle).first().coefficient

    bmr += db_sess.query(Goal).filter(Goal.id == current_user.goal).first().addition
    bmr = round(bmr)

    proteins = round(bmr * 0.25 / 4)
    fats = round(bmr * 0.3 / 9)
    carbohydrates = round(bmr * 0.45 / 4)

    return bmr, proteins, fats, carbohydrates


if __name__ == "__main__":
    main()
