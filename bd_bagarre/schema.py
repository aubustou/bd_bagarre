import graphene
import graphene_sqlalchemy

import bd_bagarre.model.books


class Book(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Book
        interfaces = (graphene.relay.Node,)


class Author(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Author
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    book = graphene.relay.Node.Field(Book)
    all_books = graphene_sqlalchemy.SQLAlchemyConnectionField(Book)


schema = graphene.Schema(query=Query, types=[Book])