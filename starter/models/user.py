"""
User Model
----------

Model module for User related functionality.
"""
# System imports
from datetime import datetime

# 3rd party imports
from cryptacular import bcrypt
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, DateTime, Unicode
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Serializer, fields

# Pyramid imports
from pyramid.compat import native_
from pyramid.authentication import b64encode

# Project imports
from . import Base, DBSession, CaseInsensitiveComparator
from ..lib.helpers import generate_secret


__all__ = ['User', 'UserProfile']

crypt = bcrypt.BCRYPTPasswordManager()


# User serializer class
class UserSerializer(Serializer):
    """Marshmallow serializer for converting User records to JSON."""
    id = fields.Integer()
    email = fields.String()
    role = fields.String()
    last_login = fields.DateTime('iso')
    updated = fields.DateTime('iso')
    created = fields.DateTime('iso')

    class Profile(Serializer):
        first_name = fields.String()
        last_name = fields.String()

    profile = fields.Nested(Profile)


# User model class
class User(Base):
    """
    The application's User model.
    """
    __tablename__ = 'users'

    ## Columns ##
    id = Column(Integer, primary_key=True)
    _email = Column('email', Unicode(255), unique=True, nullable=False)
    _password = Column('password', Unicode(60))
    role = Column(Unicode(20))
    api_token = Column(Unicode(40), default=generate_secret)
    password_reset_token = Column(Unicode(40), default=generate_secret)
    password_reset_sent = Column(DateTime)
    last_login = Column(DateTime)
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    created = Column(DateTime, default=datetime.utcnow)

    ## Associations ##
    profile = relationship('UserProfile', backref='user', uselist=False,
                           cascade='all, delete-orphan')

    ## Classmethods ##
    @classmethod
    def all(cls):
        """Return all objects."""
        return cls.query.all()

    @classmethod
    def count(cls):
        """Return a count of all objects."""
        return cls.query.count()

    @classmethod
    def filter_by(cls, **kw):
        """Filter objects by ``kw``."""
        return cls.query.filter_by(**kw)

    @classmethod
    def find(cls, id):
        """
        Return the object whose id is ``id``.

        If no object is found, a ``NoResultFound`` is raised.
        """
        return cls.filter_by(id=id).one()

    @classmethod
    def by_email(cls, email):
        """
        Return the object whose email address is ``email``.

        If no object is found, a ``NoResultFound`` is raised.
        """
        return cls.filter_by(email=email).one()

    ## Instance methods ##
    def update(self, params):
        return User.filter_by(id=self.id).update(params)

    def check_password(self, value):
        return crypt.check(self.password, value)

    ## Ojbect properties ##
    @property
    def full_name(self):
        return self.profile.full_name

    @property
    def authorization_token(self):
        return native_(b64encode("%s:%s" % (self.email, self.api_token)))

    @hybrid_property
    def email(self):
        return self._email.lower()

    @email.setter
    def email(self, value):
        self._email = value.lower()

    @email.comparator
    def email(cls):
        return CaseInsensitiveComparator(cls._email)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = crypt.encode(value)

    ## Special methods ##
    def __init__(self, email='', password=None, role='user', profile=None):
        self.email = email
        self.password = password or generate_secret()
        self.role = role
        self.profile = profile

    def __repr__(self):
        return '<User: %s>' % (self.email)

    def __json__(self, request):
        return UserSerializer(self).data


# UserProfile model class
class UserProfile(Base):
    """
    Application user's profile model.
    """
    __tablename__ = 'users_profiles'

    ## Columns ##
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    first_name = Column(Unicode(100))
    last_name = Column(Unicode(100))
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    created = Column(DateTime, default=datetime.utcnow)

    ## Ojbect properties ##
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    ## Special methods ##
    def __init__(self, **kw):
        self.user_id = kw.get('user_id')
        self.first_name = kw.get('first_name')
        self.last_name = kw.get('last_name')
