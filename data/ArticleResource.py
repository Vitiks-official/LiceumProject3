from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .Article import Article

KEYS = ["id", "title", "user", "content", "accepted"]


def abort_if_article_not_found(article_id):
    session = db_session.create_session()
    article = session.query(Article).get(article_id)
    if not article:
        abort(404, message=f"Product {article_id} not found")


class ArticleResource(Resource):
    def get(self, article_id):
        abort_if_article_not_found(article_id)
        session = db_session.create_session()
        article = session.query(Article).get(article_id)
        return jsonify({"article": article.to_dict(only=KEYS)})

    def post(self, article_id):
        abort_if_article_not_found(article_id)
        session = db_session.create_session()
        article = session.query(Article).get(article_id)
        article.accepted = True
        session.commit()
        return jsonify({"success": True})

    def delete(self, article_id):
        abort_if_article_not_found(article_id)
        session = db_session.create_session()
        article = session.query(Article).get(article_id)
        session.delete(article)
        session.commit()
        return jsonify({"success": True})
