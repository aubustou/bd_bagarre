# coding: utf-8

from bd_bagarre.database import db_session, init_db
from flask import Flask


from flask_graphql import GraphQLView


def main():
    app = Flask(__name__)
    app.debug = True

    init_db()

    import bd_bagarre.schema
    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view("graphql",
                                      schema=bd_bagarre.schema.schema,
                                      graphiql=True)
    )
    try:
        app.run()
    finally:
        db_session.remove()


if __name__ == "__main__":
    main()
