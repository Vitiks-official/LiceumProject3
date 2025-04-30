from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from data.User import User
from data.Product import Product
from data.UserResource import UserResource, UserListResource
from data.ProductResource import ProductResource, ProductListResource
from flask_restful import Api
import data.db_session as db_session
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "venom"

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
    app.run()


@app.route("/")
@app.route("/index")
def index():
    return "index page ^w^"


if __name__ == "__main__":
    main()
