"""Test suite for the application."""
from pyramid.compat import configparser
from sqlalchemy import engine_from_config
from starter.models import *
from starter.lib.settings import SETTINGS

def setUpModule():
    # Load the test settings
    settings = SETTINGS
    config = configparser.ConfigParser()
    config.read('test.ini')
    for option in config.options('app:main'):
        settings[option] = config.get('app:main', option)

    SETTINGS.update(settings)

    # Set up the database connection
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # Initialize the query property
    Base.query = DBSession.query_property()
    # Initialize the database
    Base.metadata.create_all()

def tearDownModule():
    # Remove the session
    DBSession.remove()
    # Drop the database
    Base.metadata.drop_all()

