import graphene
import graphene_sqlalchemy

import bd_bagarre.model.books


class Department(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Department
        interfaces = (graphene.relay.Node,)


class Employee(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Employee
        interfaces = (graphene.relay.Node,)


class Role(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = bd_bagarre.model.books.Role
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    # Allow only single column sorting
    all_employees = graphene_sqlalchemy.SQLAlchemyConnectionField(
        Employee, sort=Employee.sort_argument())
    # Allows sorting over multiple columns, by default over the primary key
    all_roles = graphene_sqlalchemy.SQLAlchemyConnectionField(Role)
    # Disable sorting over this field
    all_departments = graphene_sqlalchemy.SQLAlchemyConnectionField(Department, sort=None)


schema = graphene.Schema(query=Query, types=[Department, Employee, Role])