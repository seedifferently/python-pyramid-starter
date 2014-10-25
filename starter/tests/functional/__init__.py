# vim:fileencoding=utf-8:ai:ts=4:sts:et:sw=4:tw=80:
import unittest
import transaction
from webtest import TestApp
from pyramid.paster import get_app
from starter.models import *

class FuncTest(unittest.TestCase):
    def setUp(self):
        """Method called before running each test"""
        # Set up the App
        app = get_app('test.ini', 'main')
        self.testapp = TestApp(app)

    def tearDown(self):
        """Method called after running each test"""
        # Delete the app
        del self.testapp

        # Clear out the database
#        with transaction.manager:
#            UserProfile.query.delete()
#            User.query.delete()
#            for table in reversed(Base.metadata.sorted_tables):
#                DBSession.execute(table.delete())
