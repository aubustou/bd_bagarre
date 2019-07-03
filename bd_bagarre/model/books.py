import bd_bagarre.database
import sqlalchemy
from sqlalchemy.orm import backref, relationship


class Book(bd_bagarre.database.Base):
    __tablename__ = 'book'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    format_type = sqlalchemy.Column(sqlalchemy.String)
    page_number = sqlalchemy.Column(sqlalchemy.Integer)
    rating = sqlalchemy.Column(sqlalchemy.Integer, server_default=0)
    community_rating = sqlalchemy.Column(sqlalchemy.Integer, server_default=0)
    file_path = sqlalchemy.Column(sqlalchemy.String)  #array
    cover_path = sqlalchemy.Column(sqlalchemy.String)

    title = sqlalchemy.Column(sqlalchemy.String)
    series = sqlalchemy.Column(sqlalchemy.String)
    volume = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime)

    book_format = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    publisher = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    imprint = sqlalchemy.Column(sqlalchemy.String)  #foreignkey

    alternate_series = sqlalchemy.Column(sqlalchemy.String)  #array
    alternate_series_number = sqlalchemy.Column(sqlalchemy.Integer)
    story_arc = sqlalchemy.Column(sqlalchemy.String)
    series group = sqlalchemy.Column(sqlalchemy.String)
    series_complete = sqlalchemy.Column(sqlalchemy.Boolean, server_default=False)

    writer = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    penciller = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    inker = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    colorist = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    letterer = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    cover_artist = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    editor = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey

    genre = sqlalchemy.Column(sqlalchemy.String)  #array
    tags = sqlalchemy.Column(sqlalchemy.String)  #array

    age_rating = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    manga = sqlalchemy.Column(sqlalchemy.String)
    language = sqlalchemy.Column(sqlalchemy.String)
    black_and_white = sqlalchemy.Column(sqlalchemy.Boolean)
    proposed_values = sqlalchemy.Column(sqlalchemy.Boolean, server_default=False)

    summary = sqlalchemy.Column(sqlalchemy.String)
    notes = sqlalchemy.Column(sqlalchemy.String)
    review = sqlalchemy.Column(sqlalchemy.String)
    characters = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    main_character_or_team = sqlalchemy.Column(sqlalchemy.String)  #foreignkey
    teams = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    locations = sqlalchemy.Column(sqlalchemy.String)  #array  #foreignkey
    scan_information = sqlalchemy.Column(sqlalchemy.String)
    web_url = sqlalchemy.Column(sqlalchemy.String)





class Department(bd_bagarre.database.Base):
    __tablename__ = 'department'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


class Role(bd_bagarre.database.Base):
    __tablename__ = 'roles'
    role_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


class Employee(bd_bagarre.database.Base):
    __tablename__ = 'employee'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    hired_on = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.func.now())
    department_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('department.id'))
    role_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('roles.role_id'))
    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department,
        backref=backref('employees',
                        uselist=True,
                        cascade='delete,all'))
    role = relationship(
        Role,
        backref=backref('roles',
                        uselist=True,
                        cascade='delete,all'))