# coding: utf-8
import graphene
import graphene_sqlalchemy

import bd_bagarre.model.books


class Book(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Book
        interfaces = (graphene.relay.Node,)


class AuthorBookLink(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.authors.AuthorBookLink
        interfaces = (graphene.relay.Node,)


class Author(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.authors.Author
        interfaces = (graphene.relay.Node,)


class AuthorBookConnection(graphene.relay.Connection):
    class Meta:
        node = Author


class BookAuthorConnection(graphene.relay.Connection):
    class Meta:
        node = Book


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    book = graphene.relay.Node.Field(Book)
    author_book_link = graphene.relay.Node.Field(AuthorBookLink)
    all_books = graphene_sqlalchemy.SQLAlchemyConnectionField(Book)

    author = graphene.relay.Node.Field(Author)
    all_authors = graphene_sqlalchemy.SQLAlchemyConnectionField(Author)

    def resolve_book(self, args, context, info):
        return Book.get_query(context)


schema = graphene.Schema(query=Query, types=[Book, Author])