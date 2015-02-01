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
from marshmallow import Schema

# Pyramid imports
from pyramid.compat import native_
from pyramid.authentication import b64encode

# Project imports
from . import (DBSession, Base, ModelMixin, CaseInsensitiveComparator,
               JSONFieldOpts)
from ..lib.helpers import generate_secret


__all__ = ['User', 'UserProfile', 'UserJSON', 'UserProfileJSON']

crypt = bcrypt.BCRYPTPasswordManager()


# User model class
class User(ModelMixin, Base):
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
    def by_email(cls, email):
        """
        Return the object whose email address is ``email``.

        If no object is found, a ``NoResultFound`` is raised.
        """
        return cls.filter_by(email=email).one()

    ## Instance methods ##
    def check_password(self, value):
        return crypt.check(self.password, value)

    ## Object properties ##
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

# User JSON serializer class
class UserJSON(Schema):
    """Marshmallow schema mapper for serializing objects as JSON."""
    OPTIONS_CLASS = JSONFieldOpts

    class Meta:
        supported_fields = list(User._sa_class_manager.keys())
        fields = User.__table__.columns.keys()
        exclude = ('api_token', 'password', 'password_reset_sent',
                   'password_reset_token')


# UserProfile model class
class UserProfile(ModelMixin, Base):
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

    ## Object properties ##
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    ## Special methods ##
    def __init__(self, **kw):
        self.user_id = kw.get('user_id')
        self.first_name = kw.get('first_name')
        self.last_name = kw.get('last_name')

# User Profile JSON serializer class
class UserProfileJSON(Schema):
    """Marshmallow schema mapper for serializing objects as JSON."""
    OPTIONS_CLASS = JSONFieldOpts

    class Meta:
        supported_fields = list(UserProfile._sa_class_manager.keys())
        fields = UserProfile.__table__.columns.keys()
