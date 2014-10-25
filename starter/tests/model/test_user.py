# vim:fileencoding=utf-8:ai:ts=4:sts:et:sw=4:tw=80:
from unittest import TestCase
import transaction
from starter.models import *

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
        # User.all()
        self.assertEqual(len(User.all()), 2)
        self.assertIn(self.admin_user, User.all())
        self.assertIn(self.user_user, User.all())

        # User.count()
        self.assertEqual(User.count(), 2)

        # User.filter_by()
        self.assertEqual(User.filter_by(email='admin@example.com').one(),
                         self.admin_user)

        # User.find()
        self.assertEqual(User.find(self.admin_user.id), self.admin_user)

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
