#!/usr/bin/env python

from bd_bagarre.database import db_session, init_db
from flask import Flask
from bd_bagarre.schema import schema

from flask_graphql import GraphQLView


def main():
    app = Flask(__name__)
    app.debug = True

    app.add_url_rule(
        "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
    )
    init_db()
    try:
        app.run()
    finally:
        db_session.remove()


if __name__ == "__main__":
    main()
