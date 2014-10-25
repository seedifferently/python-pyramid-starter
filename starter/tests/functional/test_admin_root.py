import transaction
from . import FuncTest
from starter.models import *

class TestAdminRoot(FuncTest):
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

    def test_index(self):
        # Test unauthenticated/unauthorized access
        res = self.testapp.get('/admin/', status=302)
        res = res.follow() # Follow the redirect
        res.mustcontain('<h1>Login</h1>')
        self.assertIn(
            'Please log in before continuing.',
            res.pyquery('#flash-message').text()
        )

        # Test authenticated/unauthorized access
        form = res.form
        form['email'] = 'user@example.com'
        form['password'] = '123456'
        res = form.submit('Login')
        self.assertEqual(res.status_int, 302)
        res = res.follow() # Follow the redirect to /admin/ (unauthorized)
        res = res.follow() # Follow the redirect back to /
        res.mustcontain('<h1>Pyramid App</h1>')
        self.assertIn(
            'You are not authorized to access that location.',
            res.pyquery('#flash-message').text()
        )

        # Test authenticated/authorized access
        res = self.testapp.get(
            '/users/logout.html',
            status=302
        )
        res = self.testapp.get('/admin/', status=302)
        res = res.follow() # Follow the redirect
        # Submit login form with valid data
        form = res.form
        form['email'] = 'admin@example.com'
        form['password'] = '123456'
        res = form.submit('Login')
        self.assertEqual(res.status_int, 302)
        res = res.follow() # Follow the redirect

        res.mustcontain('<h1>Pyramid App <small>ADMIN</small></h1>')
