# System imports
import transaction
from unittest import TestCase

# 3rd Party imports
from sqlalchemy.orm.exc import NoResultFound

# Project imports
from starter.models import *
from starter.models.seeds import *

class TestUser(TestCase):
    def setUp(self):
        """Method called before running each test."""
        # Set up DB fixtures
        with transaction.manager:
            DBSession.add_all([
                User(
                    email='admin@example.com',
                    password='123456',
                    role='admin',
                    profile=UserProfile(
                        first_name='Admin',
                        last_name='User'
                    )
                ),
                User(
                    email='user@example.com',
                    password='123456',
                    profile=UserProfile(
                        first_name='User',
                        last_name='User'
                    )
                )
            ])

        self.admin_user = User.by_email('admin@example.com')
        self.user_user = User.by_email('user@example.com')

    def tearDown(self):
        """Method called after running each test."""
        # Clear out DB fixtures
        with transaction.manager:
            UserProfile.query.delete()
            User.query.delete()

    def test_classmethods(self):
        # User.find()
        self.assertEqual(User.find(self.admin_user.id), self.admin_user)

        with self.assertRaises(NoResultFound) as cm:
            User.find(9999)
        self.assertEqual('%s' % cm.exception,
                         'No User was found with primary key of: 9999')

        # User.first()
        self.assertEqual(User.first(User.email == 'admin@example.com'),
                         self.admin_user)

        # User.all()
        all_objs = User.all()
        self.assertEqual(len(all_objs), 2)
        self.assertIn(self.admin_user, all_objs)
        self.assertIn(self.user_user, all_objs)

        # User.count()
        self.assertEqual(User.count(), 2)

        # User.filter()
        self.assertEqual(User.filter(User.email == 'admin@example.com').one(),
                         self.admin_user)

        # User.filter_by()
        self.assertEqual(User.filter_by(email='admin@example.com').one(),
                         self.admin_user)

        # User.order_by()

        # User.lazy()

        # User.by_email()
        self.assertEqual(User.by_email('admin@example.com'), self.admin_user)

    def test_instancemethods(self):
        # update

        # check_password
        self.assertTrue(self.admin_user.check_password('123456'))

    def test_properties(self):
        # full_name
        self.assertEqual(self.user_user.full_name, 'User User')

        # Default role should be 'user'
        self.assertEqual(self.user_user.role, 'user')

        # Passwords should be encrypted
        self.assertNotEqual(self.admin_user.password, '123456')
        self.admin_user.password = '654321'
        self.assertNotEqual(self.admin_user.password, '654321')

    def test_specialmethods(self):
        # __repr__
        self.assertEqual(
            '%s' % self.admin_user,
            '<User: %s>' % self.admin_user.email
        )

        # __init__
        self.assertEqual(int(self.admin_user), self.admin_user.id)
