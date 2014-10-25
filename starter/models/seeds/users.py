import datetime
import transaction
from .. import DBSession, User, UserProfile


def seed_users():
    with transaction.manager:
        DBSession.add_all([
            User(
                email='user@example.com',
                password='user',
                role='user',
                profile=UserProfile(
                    first_name='John',
                    last_name='Smith'
                )
            ),
            User(
                email='superuser@example.com',
                password='superuser',
                role='superuser',
                profile=UserProfile(
                    first_name='Jane',
                    last_name='Smith'
                )
            ),
            User(
                email='admin@example.com',
                password='admin',
                role='admin',
                profile=UserProfile(
                    first_name='Mark',
                    last_name='Smith'
                )
            ),
            User(
                email='testing@example.com',
                password='',
                profile=UserProfile(
                    first_name='First',
                    last_name='Last'
                )
            )
        ])

    # Set test user's password reset params for testing
    with transaction.manager:
        User.by_email('testing@example.com').update({
            'password_reset_token': 'testing',
            'password_reset_sent': datetime.datetime.utcnow()
        })
