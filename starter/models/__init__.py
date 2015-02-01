"""
Models Module
-------------
"""
from importlib import import_module
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension
from marshmallow import SchemaOpts


# Initialize the Base and Session
Base = declarative_base()
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


# Define the Model class mixin
class ModelMixin:
    """
    The Model class mixin for the app's models.

    Provides various convenience and helper methods for SQLAlchemy declarative
    model classes. e.g.::

        # Using SQLAlchemy's defaults
        DBSession.query(User).get(1) # returns <User: 1>
        DBSession.query(User).get(0) # invalid, returns None
        DBSession.query(User).filter(User.role == 'admin').all() # returns [<User: 1>, <User: 2>, ...]

        # Using ModelMixin
        User.find(1) # returns <User: 1>
        User.find(0) # invalid, raises NoResultFound (!)
        User.all(User.role == 'admin') # returns [<User: 1>, <User: 2>, ...]

    """
    # Define the query property
    query = DBSession.query_property()

    @classmethod
    def find(cls, ident):
        """
        Convenience method for returning the object with a primary key
        identifier of ``ident``.

        .. note:: Although this method utilizes
                  :py:meth:`sqlalchemy.orm.query.Query.get`, be aware that if no
                  matching row is found it will raise
                  :py:class:`~sqlalchemy.orm.exc.NoResultFound` (in the style of
                  :py:meth:`~sqlalchemy.orm.query.Query.one`) rather than
                  simply returning ``None``.
        """
        obj = cls.query.get(ident)

        if not obj:
            raise NoResultFound('No %s was found with primary key of: %s' % (
                                cls.__name__, ident))
        else:
            return obj

    @classmethod
    def first(cls, *filters):
        """
        Convenience method for returning the first object (optionally
        :py:meth:`filter` by passing ``filters``).

        cf. :py:meth:`sqlalchemy.orm.query.Query.first`
        """
        return cls.query.filter(*filters).first()

    @classmethod
    def all(cls, *filters):
        """
        Convenience method for returning all objects (optionally
        :py:meth:`filter` by passing ``filters``).

        cf. :py:meth:`sqlalchemy.orm.query.Query.all`
        """
        return cls.query.filter(*filters).all()

    @classmethod
    def count(cls, *filters):
        """
        Convenience method for getting a count of all rows (optionally
        :py:meth:`filter` by passing ``filters``).
        """
        return DBSession.query(func.count('*')) \
                        .select_from(cls) \
                        .filter(*filters) \
                        .scalar()

    @classmethod
    def filter(cls, *criterion):
        """
        ``Model.filter(criterion)`` convenience method.

        cf. :py:meth:`sqlalchemy.orm.query.Query.filter`
        """
        return cls.query.filter(*criterion)

    @classmethod
    def filter_by(cls, **kwargs):
        """
        ``Model.filter_by(kwargs)`` convenience method.

        cf. :py:meth:`sqlalchemy.orm.query.Query.filter_by`
        """
        return cls.query.filter_by(**kwargs)

    @classmethod
    def order_by(cls, *criterion):
        """
        ``Model.order_by(criterion)`` convenience method.

        cf. :py:meth:`sqlalchemy.orm.query.Query.order_by`
        """
        return cls.query.order_by(*criterion)

    @classmethod
    def lazy(cls):
        """
        Override the default :py:meth:`sqlalchemy.orm.relationship` loading for
        all relationships to "lazy."

        cf. :py:func:`sqlalchemy.orm.lazyload`
        """
        return cls.query.options(lazyload('*'))

    ## Instance methods ##
    def update(self, values, synchronize_session='evaluate'):
        """
        ``obj.update(values)`` convenience method.

        cf. :py:meth:`sqlalchemy.orm.query.Query.update`
        """
        return self.__class__.filter_by(id=self.id).update(values,
                                                           synchronize_session)

    ## Special methods ##
    def __int__(self):
        return self.id

    def __json__(self, request):
        """
        Special method for serializing Model objects as JSON.

        Includes limited support for "sparse fieldsets" (see:
        http://jsonapi.org/format/#fetching-sparse-fieldsets) and "linked
        resource inclusion" (see: http://jsonapi.org/format/#fetching-includes).

        Expects the model's module to define a :py:class:`marshmallow.Schema`
        class with a naming convention of ``ModelNameJSON``. If not found, None
        (``null``) will be returned.
        """
        # Look for a JSON schema class for this object
        models = import_module('starter.models')
        cls = getattr(models, '%sJSON' % self.__class__.__name__, None)

        # Return None if no JSON schema class was found
        if not cls:
            return None

        # Initialize the JSON class
        json = cls()
        # Back up fields attr, in case it's modified via the include param
        original_fields = json.Meta.fields[:]

        # Partial support for linked resource inclusion
        # http://jsonapi.org/format/#fetching-includes
        if request.GET.get('include'):
            json.Meta.fields.extend(
                [field for field in request.GET['include'].split(',')
                 if field in getattr(json.Meta, 'supported_fields', []) and
                 field not in getattr(json.Meta, 'fields', []) and
                 field not in getattr(json.Meta, 'exclude', [])]
            )

        # Partial support for sparse fieldsets
        # http://jsonapi.org/format/#fetching-sparse-fieldsets
        if request.GET.get('fields'):
            json.only = [
                field for field in request.GET['fields'].split(',')
                if field in getattr(json.Meta, 'supported_fields', []) and
                   field not in getattr(json.Meta, 'exclude', [])
            ]

        # Initialize the serialized data
        data = json.dump(self).data

        # Restore the original fields attr if it was modified
        if json.Meta.fields != original_fields:
            json.Meta.fields = original_fields

        return data


# Adds a "supported_fields" option to Marshmallow schema Meta options
class JSONFieldOpts(SchemaOpts):
    """
    Custom :py:class:`marshmallow.SchemaOpts` class which defines a
    ``supported_fields`` option.
    """
    def __init__(self, meta):
        SchemaOpts.__init__(self, meta)
        self.supported_fields = getattr(meta, 'supported_fields', None)


# SQLAlchemy extensions
class CaseInsensitiveComparator(Comparator):
    """Custom comparator for making sure matches are case-insensitive."""
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


# Load model objects
from .user import *
