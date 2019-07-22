# coding: utf-8
import graphene
import graphene_sqlalchemy

import bd_bagarre.model.books


class Book(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Book
        interfaces = (graphene.relay.Node,)

    writers = graphene.List('bd_bagarre.schema.Author')
    pencilers = graphene.List('bd_bagarre.schema.Author')
    authors = graphene.List('bd_bagarre.schema.Author')

    def resolve_authors(parent, info):
        return [a.author for a in parent.authors]

    def resolve_writers(parent, info):
        return [a.author for a in parent.authors if a.role == 'writer']

    def resolve_pencilers(parent, info):
        return [a.author for a in parent.authors if a.role == 'penciler']


class BookFile(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.BookFile
        interfaces = (graphene.relay.Node,)


class Publisher(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Publisher
        interfaces = (graphene.relay.Node,)


class AuthorBookLink(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.authors.AuthorBookLink
        interfaces = (graphene.relay.Node,)


class Author(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.authors.Author
        interfaces = (graphene.relay.Node,)


class BookFileConnection(graphene.relay.Connection):
    class Meta:
        node = BookFile


class PublisherConnection(graphene.relay.Connection):
    class Meta:
        node = Publisher


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


schema = graphene.Schema(query=Query, types=[Book, Author])