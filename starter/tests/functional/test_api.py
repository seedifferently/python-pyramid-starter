import datetime
import transaction
from pyramid.authentication import b64encode
from pyramid.compat import native_
from pyramid_mailer import get_mailer

from . import FuncTest
from starter.models import *

class TestAPIRoot(FuncTest):
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

    def test_index(self): # /api/
        headers = {'Accept': 'application/json'}
        res = self.testapp.get('/api/', headers=headers, status=200)
        self.assertEqual(res.json, {'data': 'data'})

    def test_me(self): # /api/me.json
        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.get('/api/me.json', headers=headers, status=200)
        self.assertEqual(res.json, {'data': None})

        # Test authenticated/authorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/me.json', headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertIn('email', res.json['data'])
        self.assertEqual(res.json['data']['email'], 'user@example.com')


class TestAPIUsers(FuncTest):
    def setUp(self):
        """Method called before running each test"""
        # Set up the FuncTest
        super(TestAPIUsers, self).setUp()

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
        """Method called after running each test"""
        # Clear out DB fixtures
        with transaction.manager:
            UserProfile.query.delete()
            User.query.delete()

        # Tear down the FuncTest
        super(TestAPIUsers, self).tearDown()

    def test_options(self):
        res = self.testapp.options('/api/users/', status=204)
        # TODO: verify headers

    def test_index(self):
        # Build 100 new User records, for testing pagination
        users = [
            User(
                email='user+%s@example.com' % i,
                password='123456',
                profile=UserProfile(
                    first_name='User%s' % i,
                    last_name='User',
                )
            )
            for i in range(100)
        ]

        with transaction.manager:
            DBSession.add_all(users)

        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.get('/api/users/', headers=headers, status=401)
        self.assertFalse(res.body)

        # Test authenticated/unauthorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/users/', headers=headers, status=403)
        self.assertFalse(res.body)

        # Test authenticated/authorized access
        token = b64encode('%s:%s' % (self.admin_user.email,
                                     self.admin_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/users/', headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertEqual(len(res.json['data']), 100)
        self.assertIn('@example.com', res.json['data'][0]['email'])
        self.assertIn('meta', res.json)
        self.assertEqual(res.json['meta']['page'], 1)
        self.assertEqual(res.json['meta']['page_count'], 2)
        self.assertEqual(res.json['meta']['item_count'], 102)
        self.assertEqual(res.json['meta']['items_per_page'], 100)

        # Test authenticated/authorized access -- page 2 (.json extension)
        res = self.testapp.get('/api/users.json?page=2', headers=headers,
                               status=200)
        self.assertIn('data', res.json)
        self.assertEqual(len(res.json['data']), 2)
        self.assertIn('@example.com', res.json['data'][0]['email'])
        self.assertIn('meta', res.json)
        self.assertEqual(res.json['meta']['page'], 2)
        self.assertEqual(res.json['meta']['page_count'], 2)
        self.assertEqual(res.json['meta']['item_count'], 102)
        self.assertEqual(res.json['meta']['items_per_page'], 100)

    def test_create(self):
        data = {'email': 'test@example.com', 'password': '654321',
                'profile': {'first_name': 'John', 'last_name': 'Smith'}}

        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/', data, headers=headers,
                                     status=401)
        self.assertFalse(res.body)

        # Test authenticated/unauthorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.post_json('/api/users/', data, headers=headers,
                                     status=403)
        self.assertFalse(res.body)

        # Test authenticated/authorized access -- missing data
        token = b64encode('%s:%s' % (self.admin_user.email,
                                     self.admin_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.post_json('/api/users', {}, headers=headers,
                                     status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'], 'Missing value')

        # Test authenticated/authorized access -- invalid data
        data['email'] = 'invalid'
        res = self.testapp.post_json('/api/users', data, headers=headers,
                                     status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'],
                         'An email address must contain a single @')

        # Test authenticated/authorized access -- duplicate email
        data['email'] = 'user@example.com'
        res = self.testapp.post_json('/api/users', data, headers=headers,
                                     status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'],
                         'Email address must be unique')

        # Test authenticated/authorized access -- valid data (trailing slash)
        data['email'] = 'TEST-SLASH@EXAMPLE.COM'
        res = self.testapp.post_json('/api/users/', data, headers=headers,
                                     status=201)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('id', res.json['data'])
        # Verify email was downcased
        self.assertEqual(res.json['data']['email'], 'test-slash@example.com')

        # Test authenticated/authorized access -- valid data (.json extension)
        data['email'] = 'test.json@example.com'
        res = self.testapp.post_json('/api/users.json', data, headers=headers,
                                     status=201)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('id', res.json['data'])
        self.assertEqual(res.json['data']['email'], 'test.json@example.com')

        # Re-read the resource to verify create
        id = res.json['data']['id']
        res = self.testapp.get('/api/users/%s' % id, headers=headers,
                               status=200)
        self.assertIn('data', res.json)
        self.assertEqual(res.json['data']['email'], 'test.json@example.com')
        self.assertEqual(res.json['data']['profile']['first_name'], 'John')
        self.assertEqual(res.json['data']['profile']['last_name'], 'Smith')

    def test_read(self):
        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.get('/api/users/%s' % self.user_user.id,
                               headers=headers, status=401)
        self.assertFalse(res.body)

        # Test authenticated/authorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/users/%s' % self.user_user.id,
                               headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertEqual(res.json['data']['email'], 'user@example.com')

        # Test authenticated/authorized access (.json extension)
        res = self.testapp.get('/api/users/%s.json' % self.user_user.id,
                               headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertEqual(res.json['data']['email'], 'user@example.com')

    def test_update(self):
        data = {'email': 'test@example.com', 'password': 'secret',
                'profile': {'first_name': 'John', 'last_name': 'Smith'}}

        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     data, headers=headers, status=401)
        self.assertFalse(res.body)

        # Test authenticated/unauthorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     data, headers=headers, status=403)
        self.assertFalse(res.body)

        # Test authenticated/authorized access -- invalid request method
        token = b64encode('%s:%s' % (self.admin_user.email,
                                     self.admin_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.post_json('/api/users/%s/no' % self.user_user.id,
                                     data, headers=headers, status=404)

        # Test authenticated/authorized access -- invalid user id
        res = self.testapp.post_json('/api/users/999', data, headers=headers,
                                     status=404)

        # Test authenticated/authorized access -- missing data
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     {}, headers=headers, status=400)

        # Test authenticated/authorized access -- invalid data
        data['role'] = 'invalid'
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     data, headers=headers, status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['role'], 'Invalid value')

        # Test authenticated/authorized access -- duplicate email
        data['role'] = 'user'
        data['email'] = 'admin@example.com'
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     data, headers=headers, status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'],
                         'Email address must be unique')

        # Test authenticated/authorized access -- valid data
        data['email'] = 'TEST@EXAMPLE.COM'
        res = self.testapp.post_json('/api/users/%s' % self.user_user.id,
                                     data, headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        # Verify email was downcased
        self.assertEqual(res.json['data']['email'], 'test@example.com')
        self.assertEqual(res.json['data']['profile']['last_name'], 'Smith')

        # Re-read the resource to verify update
        res = self.testapp.get('/api/users/%s' % self.user_user.id,
                               headers=headers, status=200)
        self.assertIn('data', res.json)
        # Verify email was downcased
        self.assertEqual(res.json['data']['email'], 'test@example.com')
        self.assertEqual(res.json['data']['profile']['first_name'], 'John')
        self.assertEqual(res.json['data']['profile']['last_name'], 'Smith')

        # Test authenticated/authorized access -- valid data (.json extension)
        data['profile']['last_name'] = 'Last'
        res = self.testapp.post_json('/api/users/%s.json' % self.user_user.id,
                                     data, headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertEqual(res.json['data']['email'], 'test@example.com')
        self.assertEqual(res.json['data']['profile']['last_name'], 'Last')

    def test_delete(self):
        # Test unauthenticated/unauthorized access
        headers = {'Accept': 'application/json'}
        res = self.testapp.delete_json('/api/users/%s' % self.user_user.id,
                               headers=headers, status=401)
        self.assertFalse(res.body)

        # Test authenticated/unauthorized access
        token = b64encode('%s:%s' % (self.user_user.email,
                                     self.user_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.delete_json('/api/users/%s' % self.user_user.id,
                               headers=headers, status=403)
        self.assertFalse(res.body)

        # Test authenticated/authorized access -- invalid request method
        token = b64encode('%s:%s' % (self.admin_user.email,
                                     self.admin_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/users/%s/test' % self.user_user.id,
                               headers=headers, status=404)

        # Test authenticated/authorized access -- invalid user id
        res = self.testapp.delete_json('/api/users/9999', headers=headers,
                                       status=404)

        # Test authenticated/authorized access -- valid
        res = self.testapp.delete_json('/api/users/%s' % self.user_user.id,
                                       headers=headers, status=204)

        # Re-read the resource to verify delete
        res = self.testapp.get('/api/users/%s' % self.user_user.id,
                               headers=headers, status=404)

        # Test authenticated/authorized access -- valid (.json extension)
        res = self.testapp.delete_json(
            '/api/users/%s.json' % self.admin_user.id,
            headers=headers,
            status=204
        )

    def test_login(self):
        # Test missing credentials
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/login', {}, headers=headers,
                                     status=422)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['errors']['email'],
                         'Please enter an email address')
        self.assertEqual(res.json['errors']['password'], 'Please enter a value')
        self.assertEqual(res.json['data'], None)

        # Test invalid email
        res = self.testapp.post_json('/api/users/login', {'email': 'test@'},
                                     headers=headers, status=422)
        self.assertIn('errors', res.json)
        self.assertEqual(
            res.json['errors']['email'],
            'The domain portion of the email address is invalid '
            '(the portion after the @: )'
        )
        self.assertEqual(res.json['errors']['password'], 'Please enter a value')
        self.assertEqual(res.json['data'], None)

        # Test invalid password
        res = self.testapp.post_json(
            '/api/users/login',
            {'email': self.user_user.email, 'password': '654321'},
            headers=headers,
            status=422
        )
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['errors']['_global'],
                         'Invalid email or password.')
        self.assertEqual(res.json['data'], None)

        # Test valid credentials
        res = self.testapp.post_json(
            '/api/users/login',
            {'email': self.user_user.email, 'password': '123456'},
            headers=headers,
            status=200
        )
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('last_login', res.json['data'])
        self.assertEqual(res.json['data']['id'], 2)
        self.assertEqual(res.json['data']['email'], 'user@example.com')
        self.assertEqual(res.json['data']['role'], 'user')
        self.assertEqual(res.json['data']['api_token'],
                         self.user_user.api_token)
        self.assertEqual(res.json['data']['profile']['first_name'], 'User')
        self.assertEqual(res.json['data']['profile']['last_name'], 'User')

        # Test valid credentials (.json extension)
        res = self.testapp.post_json(
            '/api/users/login.json',
            {'email': self.user_user.email, 'password': '123456'},
            headers=headers,
            status=200
        )
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('last_login', res.json['data'])
        self.assertEqual(res.json['data']['id'], 2)

    def test_register(self):
        data = {'email': 'test@example.com', 'password': '654321',
                'confirm': '654321', 'profile': {'first_name': 'John',
                                                 'last_name': 'Smith'}}

        # Test missing data
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/register', {}, headers=headers,
                                     status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'], 'Missing value')

        # Test invalid data
        data['email'] = 'invalid'
        res = self.testapp.post_json('/api/users/register', data,
                                     headers=headers, status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'],
                         'An email address must contain a single @')

        # Test duplicate email
        data['email'] = 'user@example.com'
        res = self.testapp.post_json('/api/users/register', data,
                                     headers=headers, status=422)
        self.assertIn('data', res.json)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors']['email'],
                         'Email address is already registered')

        # Test valid data
        data['email'] = 'TEST@EXAMPLE.COM'
        res = self.testapp.post_json('/api/users/register', data,
                                     headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('id', res.json['data'])
        self.assertEqual(res.json['data']['email'], 'test@example.com')

        # Re-read the resource to verify register
        id = res.json['data']['id']
        token = b64encode('%s:%s' % (self.admin_user.email,
                                     self.admin_user.api_token))
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token %s' % native_(token)}
        res = self.testapp.get('/api/users/%s' % id, headers=headers,
                               status=200)
        self.assertIn('data', res.json)
        self.assertEqual(res.json['data']['email'], 'test@example.com')
        self.assertEqual(res.json['data']['profile']['first_name'], 'John')
        self.assertEqual(res.json['data']['profile']['last_name'], 'Smith')

        # Test valid data (.json extension)
        data['email'] = 'test-json@example.com'
        res = self.testapp.post_json('/api/users/register.json', data,
                                     headers=headers, status=200)
        self.assertIn('data', res.json)
        self.assertIn('profile', res.json['data'])
        self.assertIn('id', res.json['data'])
        self.assertEqual(res.json['data']['email'], 'test-json@example.com')

    def test_forgot_password(self):
        # Test missing email
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/forgot_password', {},
                                     headers=headers, status=422)
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['errors']['email'],
                         'Please enter an email address')
        self.assertEqual(res.json['data'], None)

        # Test improperly formatted email
        res = self.testapp.post_json(
            '/api/users/forgot_password',
            {'email': 'test@'},
            headers=headers,
            status=422
        )
        self.assertIn('errors', res.json)
        self.assertEqual(
            res.json['errors']['email'],
            'The domain portion of the email address is invalid '
            '(the portion after the @: )'
        )
        self.assertEqual(res.json['data'], None)

        # Test invalid email
        res = self.testapp.post_json(
            '/api/users/forgot_password',
            {'email': 'invalid@example.com'},
            headers=headers,
            status=422
        )
        self.assertIn('errors', res.json)
        self.assertEqual(
            res.json['errors']['_global'],
            'Invalid email address.'
        )
        self.assertEqual(res.json['data'], None)

        # Test valid email (.json extension)
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json(
            '/api/users/forgot_password.json',
            {'email': self.user_user.email},
            headers=headers,
            status=200
        )
        self.assertIn('errors', res.json)
        self.assertEqual(res.json['errors'], {})
        self.assertEqual(res.json['data'], None)

        # Check the email
        registry = self.testapp.app.registry
        mailer = get_mailer(registry)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject, 'Starter Password Reset')
        self.assertIn('Please follow the instructions at the following link ' +
                      'to reset your password:', mailer.outbox[0].body)

    def test_reset_password(self):
        data = {'token': 'arst', 'email': 'user@example.com',
                'password': '654321', 'confirm': '654321'}

        # Test invalid data
        headers = {'Accept': 'application/json'}
        res = self.testapp.post_json('/api/users/reset_password', {},
                                     headers=headers, status=422)
        self.assertEqual(res.json['errors']['email'],
                         'Missing value')
        self.assertEqual(res.json['data'], None)

        # Test invalid token
        res = self.testapp.post_json('/api/users/reset_password', data,
                                     headers=headers, status=422)
        self.assertEqual(res.json['errors']['_global'],
                         'Could not verify reset parameters.')
        self.assertEqual(res.json['data'], None)

        # Test reset token expired
        data['token'] = self.user_user.password_reset_token
        res = self.testapp.post_json('/api/users/reset_password.json', data,
                                     headers=headers, status=422)
        self.assertEqual(res.json['errors']['_global'],
                         'Could not verify reset parameters.')
        self.assertEqual(res.json['data'], None)

        # Test passwords don't match
        data['confirm'] = '123456'
        res = self.testapp.post_json('/api/users/reset_password', data,
                                     headers=headers, status=422)
        self.assertEqual(res.json['errors']['confirm'],
                         'Fields do not match')
        self.assertEqual(res.json['data'], None)

        # Test valid data (.json extension)
        data['confirm'] = '654321'
        data['token'] = self.user_user.password_reset_token
        with transaction.manager:
            self.user_user.update({
                'password_reset_sent': datetime.datetime.utcnow()
            })
        res = self.testapp.post_json('/api/users/reset_password.json', data,
                                     headers=headers, status=200)
        self.assertEqual(res.json['data'], None)
        self.assertEqual(res.json['errors'], {})
