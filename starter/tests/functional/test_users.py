# System imports
from datetime import datetime, timedelta

# Pyramid imports
from pyramid_mailer import get_mailer

import transaction
from . import FuncTest
from starter.models import *

class TestUsers(FuncTest):
    def setUp(self):
        """Method called before running each test."""
        # Set up the FuncTest
        super(self.__class__, self).setUp()

        # Set up DB fixtures
        with transaction.manager:
            DBSession.add_all([
                User(
                    email='admin@example.com',
                    password='123456',
                    role='admin',
                    profile=UserProfile(
                        first_name='Admin',
                        last_name='User',
                    )
                ),
                User(
                    email='user@example.com',
                    password='123456',
                    profile=UserProfile(
                        first_name='User',
                        last_name='User',
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

        # Tear down the FuncTest
        super(self.__class__, self).tearDown()

    def test_login(self):
        res = self.testapp.get('/users/login.html', status=200)
        res.mustcontain('<h1>Login</h1>')

        # GET login with invalid params
        res = self.testapp.get(
            '/users/login.html?email=admin@example.com',
            status=200
        )
        self.assertIn(
            'Invalid email or password.',
            res.pyquery('#flash-message').text()
        )

        # Submit login form with invalid email
        form = res.form
        form['email'] = 'invalid@example.com'
        form['password'] = '123456'
        res = form.submit('Login')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Invalid email or password.',
            res.pyquery('#flash-message').text()
        )

        # Submit login form with invalid password
        form = res.form
        form['email'] = 'admin@example.com'
        form['password'] = '654321'
        res = form.submit('Login')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Invalid email or password.',
            res.pyquery('#flash-message').text()
        )

        # Submit login form with valid data
        form = res.form
        form['email'] = 'admin@example.com'
        form['password'] = '123456'
        res = form.submit('Login')
        self.assertEqual(res.status_int, 302)
        res = res.follow() # Follow the redirect
        res.mustcontain('<h1>Pyramid App</h1>')

        # Visit login page again
        res = self.testapp.get('/users/login.html', status=302)
        res = res.follow() # Follow the redirect
        # Verify already logged in
        self.assertIn(
            'You are already logged in.',
            res.pyquery('#flash-message').text()
        )

    def test_logout(self):
        # Login
        res = self.testapp.get(
            '/users/login.html?email=admin@example.com&password=123456',
            status=302
        )
        # Check that the auth cookie was set
        self.assertNotEqual(self.testapp.cookies['auth_tkt'], '')

        # Logout
        res = self.testapp.get('/users/logout.html', status=302)
        # Check that the auth cookie was cleared
        self.assertFalse('auth_tkt' in self.testapp.cookies)

    def test_register(self):
        res = self.testapp.get('/users/register.html', status=200)

        # Submit form with invalid data
        form = res.forms['register-form']
        form['profile.first_name'] = 'Test'
        form['profile.last_name'] = 'Ing'
        form['email'] = 'test@example.com'
        form['password'] = '123456'
        form['confirm'] = '654321'
        res = form.submit('Register')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Please correct the specified errors.',
            res.pyquery('#flash-message').text()
        )

        # Submit form with used email
        form = res.forms['register-form']
        form['profile.first_name'] = 'Test'
        form['profile.last_name'] = 'Ing'
        form['email'] = 'user@example.com'
        form['password'] = '123456'
        form['confirm'] = '123456'
        res = form.submit('Register')
        self.assertEqual(res.status_int, 200)
        res.mustcontain('Email address is already registered')

        # Submit form with valid data
        form = res.forms['register-form']
        form['profile.first_name'] = 'Test'
        form['profile.last_name'] = 'Ing'
        form['email'] = 'test@example.com'
        form['password'] = '123456'
        form['confirm'] = '123456'
        res = form.submit('Register')
        self.assertEqual(res.status_int, 302)
        res = res.follow() # Follow the redirect
        res.mustcontain('<h1>Pyramid App</h1>')

        # Verify user was logged in
        res = self.testapp.get('/users/register.html', status=302)
        res = res.follow() # Follow the redirect
        self.assertIn(
            'You are already logged in.',
            res.pyquery('#flash-message').text()
        )

    def test_forgot_password(self):
        res = self.testapp.get('/users/forgot_password.html', status=200)

        # Submit form with invalid data
        form = res.forms['forgot-password-form']
        form['email'] = 'test'
        res = form.submit('Submit')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Please correct the specified errors.',
            res.pyquery('#flash-message').text()
        )

        # Submit form with invalid email
        form = res.forms['forgot-password-form']
        form['email'] = 'test@example.com'
        res = form.submit('Submit')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Invalid email address.',
            res.pyquery('#flash-message').text()
        )

        # Submit form with valid data
        form = res.forms['forgot-password-form']
        form['email'] = 'user@example.com'
        res = form.submit('Submit')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Password reset link has been emailed to you.',
            res.pyquery('#flash-message').text()
        )

        # Check the email
        registry = self.testapp.app.registry
        mailer = get_mailer(registry)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject, 'Starter Password Reset')
        self.assertIn('Please follow the instructions at the following link ' +
                      'to reset your password:', mailer.outbox[0].body)

    def test_reset_password(self):
        res = self.testapp.get('/users/reset_password.html', status=200)

        # Submit form with invalid data
        form = res.forms['reset-password-form']
        form['token'] = 'arst'
        form['email'] = 'test@example.com'
        form['password'] = '123456'
        form['confirm'] = '654321'
        res = form.submit('Reset Password')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Please correct the specified errors.',
            res.pyquery('#flash-message').text()
        )

        # Submit form with expired token
        with transaction.manager:
            self.user_user.update({
                'password_reset_token': 'arst',
                'password_reset_sent': datetime.utcnow() - timedelta(days=8)
            })

        form = res.forms['reset-password-form']
        form['token'] = 'arst'
        form['email'] = 'user@example.com'
        form['password'] = '123456'
        form['confirm'] = '123456'
        res = form.submit('Reset Password')
        self.assertEqual(res.status_int, 200)
        self.assertIn(
            'Could not verify reset parameters.',
            res.pyquery('#flash-message').text()
        )

        # Submit form with valid data
        with transaction.manager:
            self.user_user.update({
                'password_reset_token': 'arst',
                'password_reset_sent': datetime.utcnow() - timedelta(days=3)
            })

        form = res.forms['reset-password-form']
        form['token'] = 'arst'
        form['email'] = 'user@example.com'
        form['password'] = '123456'
        form['confirm'] = '123456'
        res = form.submit('Reset Password')
        self.assertEqual(res.status_int, 302)
        res = res.follow() # Follow the redirect
        # Verify user is ready to log in
        res.mustcontain('<h1>Login</h1>')
        self.assertIn(
            'Your password was successfully changed.',
            res.pyquery('#flash-message').text()
        )
