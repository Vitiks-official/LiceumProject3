from flask_restful import Resource, abort, reqparse
from flask import jsonify
from . import db_session
from .Product import Product

KEYS = ["name", "calories", "proteins", "fats", "carbohydrates", "public", "accepted"]

parser = reqparse.RequestParser()
parser.add_argument("name", required=True)
parser.add_argument("calories", required=True, type=int)
parser.add_argument("proteins", required=True, type=int)
parser.add_argument("fats", required=True, type=int)
parser.add_argument("carbohydrates", required=True, type=int)


# Function for checking the existence of a product
def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


# Resource for interaction with a Product by id
class ProductResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        return jsonify({"product": product.to_dict(only=KEYS)})

    def post(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        product.accepted = True
        session.commit()
        return jsonify({"success": True})

    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({"success": True})


# Resource for interaction with Products without id
class ProductListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify({"products": [item.to_dict(only=KEYS) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            name=args["name"],
            calories=args["calories"],
            proteins=args["proteins"],
            fats=args["fats"],
            carbohydrates=args["carbohydrates"]
        )
        session.add(product)
        session.commit()
        return jsonify({"id": product.id})
