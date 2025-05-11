from flask_restful import Resource, abort, reqparse
from flask import jsonify
from . import db_session
from .User import User

KEYS = ["surname", "name", "age", "gender", "weight", "height", "goal", "email", "is_admin"]

parser = reqparse.RequestParser()
parser.add_argument("surname", required=True)
parser.add_argument("name", required=True)
parser.add_argument("age", required=True, type=int)
parser.add_argument("gender", required=True, type=int)
parser.add_argument("weight", required=True, type=int)
parser.add_argument("height", required=True, type=int)
parser.add_argument("goal", required=False, type=int)
parser.add_argument("email", required=True)
parser.add_argument("is_admin", required=False, type=bool, default=False)
parser.add_argument("password", required=True)


# Function for checking the existence of a user
def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


# Resource for interaction with a User by id
class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({"user": user.to_dict(only=KEYS)})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({"success": True})


# Resource for interaction with Users without id
class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({"users": [item.to_dict(only=KEYS) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args["surname"],
            name=args["name"],
            age=args["age"],
            gender=args["gender"],
            weight=args["weight"],
            height=args["height"],
            goal=args["goal"],
            email=args["email"],
            is_admin=args["is_admin"]
        )
        user.set_password(args["password"])
        session.add(user)
        session.commit()
        return jsonify({"id": user.id})
