"""
Models Module
-------------
"""
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension


# Initialize SQLAlchemy
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

# Set up the query property
Base.query = DBSession.query_property()

# SQLAlchemy extensions
class CaseInsensitiveComparator(Comparator):
    """Custom comparator for making sure matches are case-insensitive."""
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


# Load model objects
from .user import *
