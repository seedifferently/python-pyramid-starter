"""
API Users View (/api/users/)
----------------------------
"""
# System imports
import logging
from datetime import datetime, timedelta

# 3rd party imports
import transaction
from paginate_sqlalchemy import SqlalchemyOrmPage
from html2text import html2text

# Pyramid imports
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.renderers import render
from pyramid_handlers import action
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

# Project imports
from . import APIView
from starter.models import DBSession, NoResultFound, User, UserProfile
from starter.lib.helpers import generate_secret
from starter.lib.validation import (validate, Int, Email, UnicodeString,
                                    UserCreateSchema, UserUpdateSchema,
                                    UserRegisterForm, UserResetPasswordForm)

logger = logging.getLogger(__name__)

class APIUsers(APIView):
    """
    The "APIUsers" view handler class.

    Responsible for JSON requests to the ``/api/users/`` routes.
    """
    @action(renderer='json', permission='admin_permissions')
    @validate(validators=dict(page=Int(min=1)), methods=['GET'])
    def index(self):
        """
        List all users.

        :param int page: The page number to load (e.g. ``/api/users/?page=2``).

        :returns: A JSON object containing:

            :data: A list of ``User`` objects.
            :meta: Pagination information.

        Example request::

            http -j :/api/users/ Authorization:"Token ..."

        Example response:

        .. code-block:: json

            {
                "data": [
                    {
                        "created": "2014-09-19T12:34:07.937062+00:00",
                        "email": "user@example.com",
                        "id": 1,
                        "last_login": "2014-09-19T12:47:08.301640+00:00",
                        "profile": {
                            "first_name": "John",
                            "last_name": "Smith"
                        },
                        "role": "user",
                        "updated": "2014-09-19T12:47:08.303298+00:00"
                    },
                    {
                        "created": "2014-09-19T12:34:07.938278+00:00",
                        "email": "superuser@example.com",
                        "id": 2,
                        "last_login": null,
                        "profile": {
                            "first_name": "Jane",
                            "last_name": "Smith"
                        },
                        "role": "superuser",
                        "updated": "2014-09-19T12:34:07.938270+00:00"
                    }
                ],
                "meta": {
                    "item_count": 2,
                    "items_per_page": 100,
                    "page": 1,
                    "page_count": 1
                }
            }
        """
        # Initialize request variables
        request = self.request
        params = self.validation_results

        meta = {}

        # Initialize pager
        page = SqlalchemyOrmPage(User.query,
                                 page=params.get('page', 1),
                                 items_per_page=self.items_per_page,
                                 item_count=User.count())

        # Build "meta" object
        for key in ['page', 'page_count', 'item_count', 'items_per_page']:
            meta[key] = getattr(page, key)

        return dict(data=page.items, meta=meta)

    @action(renderer='json', permission='superuser_permissions')
    @validate(UserCreateSchema, allow_json=True)
    def create(self):
        """
        Create a user.

        :returns: A JSON object containing:

            :data:   An object reflecting the created user.
            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/ email=email@example.com password=secret profile:='{"first_name": "John", "last_name": "Smith"}' Authorization:"Token ..."

        Example response:

        .. code-block:: json

            {
                "errors": {},
                "data": {
                    "created": "2014-09-23T09:38:25.131009+00:00",
                    "email": "email@example.com",
                    "id": 1,
                    "last_login": null,
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user",
                    "updated": "2014-09-23T09:38:25.130992+00:00"
                }
            }
        """
        # Initialize request variables
        request = self.request
        params = self.validation_results
        errors = self.validation_errors

        user = None

        if errors:
            request.response.status = '422 Unprocessable Entity'
        else:
            try:
                user = User(params['email'], params['password'],
                            role=params['role'])
                user.profile = UserProfile(**params['profile'])

                DBSession.add(user)
                DBSession.flush()
            except Exception as exc:
                # Prepare the "error" response
                user = None

                if 'unique' in str(exc).lower():
                    errors['email'] = 'Email address must be unique'
                    request.response.status = '422 Unprocessable Entity'
                else:
                    errors['_global'] = 'Unable to process create'
                    logger.error('Failed to create user: %s' % exc)
                    request.response.status = '500 Internal Server Error'
            else:
                request.response.status = '201 Created'

        return dict(data=user, errors=errors)

    @action(renderer='json', permission='user_permissions')
    def read(self):
        """
        Read a user.

        :returns: A JSON object containing:

            :data: An object reflecting the requested user.

        Example request::

            http -j :/api/users/1 Authorization:"Token ..."

        Example response:

        .. code-block:: json

            {
                "data": {
                    "created": "2014-09-23T09:38:25.131009+00:00",
                    "email": "email@example.com",
                    "id": 1,
                    "last_login": "2014-09-23T09:41:25.131009+00:00",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user",
                    "updated": "2014-09-23T09:38:25.130992+00:00"
                }
            }
        """
        # Initialize request variables
        request = self.request
        id = int(request.matchdict['id'])

        # Load the user
        try:
            user = User.find(id)
        except NoResultFound:
            raise HTTPNotFound

        return dict(data=user)

    @action(renderer='json', permission='superuser_permissions')
    @validate(UserUpdateSchema, allow_json=True)
    def update(self):
        """
        Update a user.

        :returns: A JSON object containing:

            :data:    An object reflecting the updated user.
            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/1 email=email@example.com password=secret profile:='{"first_name": "John", "last_name": "Smith"}' Authorization:"Token ..."

        Example response:

        .. code-block:: json

            {
                "data": {
                    "created": "2014-09-19T12:34:07.937062+00:00",
                    "email": "email@example.com",
                    "id": 1,
                    "last_login": "2014-09-19T12:47:08.301640+00:00",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user",
                    "updated": "2014-09-24T11:47:00.648593+00:00"
                },
                "errors": {}
            }
        """
        # Initialize request variables
        request = self.request
        id = int(request.matchdict['id'])
        params = self.validation_results
        errors = self.validation_errors

        user = None

        # Load the user
        try:
            user = User.find(id)
        except NoResultFound:
            raise HTTPNotFound

        if errors:
            user = None
            request.response.status = '422 Unprocessable Entity'
        elif not params:
            # There doesn't seem to be any data posted
            raise HTTPBadRequest
        else:
            try:
                # Pop profile
                profile = params.pop('profile', {})

                # Update the user
                for key, value in params.items():
                    if value:
                        setattr(user, key, value)

                DBSession.flush()

                if profile:
                    # Update the profile
                    for key, value in profile.items():
                        if value:
                            setattr(user.profile, key, value)

                    DBSession.flush()
            except Exception as exc:
                # Prepare the "error" response
                user = None

                if 'unique' in str(exc).lower():
                    errors['email'] = 'Email address must be unique'
                    request.response.status = '422 Unprocessable Entity'
                else:
                    errors['_global'] = 'Unable to process update'
                    logger.error('Failed to update user: %s' % exc)
                    request.response.status = '500 Internal Server Error'

        return dict(data=user, errors=errors)

    @action(renderer='json', permission='admin_permissions')
    def delete(self):
        """
        Delete a user.

        Example request::

            http -j DELETE :/api/users/1 Authorization:"Token ..."
            http -j :/api/users/1/delete Authorization:"Token ..."

        Example response::

            HTTP/1.1 204 No Content
        """
        # Initialize request variables
        request = self.request
        id = int(request.matchdict['id'])

        try:
            # Delete the user
            user = User.find(id)
            DBSession.delete(user)
        except NoResultFound:
            raise HTTPNotFound
        else:
            return Response(status='204 No Content',
                            content_type='application/json')

    @action(renderer='json')
    @validate(validators=dict(email=Email(not_empty=True),
                              password=UnicodeString(not_empty=True)),
              allow_json=True)
    def login(self):
        """
        Log in a user.

        :returns: A JSON object containing:

            :data:    An object reflecting the logged in user.
            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/login email=user@example.com password=user

        Example response:

        .. code-block:: json

            {
                "data": {
                    "api_token": "1a2b3c4d5e",
                    "email": "user@example.com",
                    "id": 1,
                    "last_login": "2014-10-23T17:46:31.491909",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user"
                },
                "errors": {}
            }
        """
        # Initialize request variables
        request = self.request
        params = self.validation_results or request.POST
        errors = self.validation_errors
        data = None

        # Set up response variables
        email = params.get('email')
        password = params.get('password')

        # Check and process form submission
        if errors:
            request.response.status = '422 Unprocessable Entity'
        else:
            # If user validates, set header and redirect
            user = User.filter_by(email=email).first()

            if user and user.check_password(password):
                # Update last login timestamp
                user.last_login = datetime.utcnow()

                data = dict(id=user.id, email=user.email, role=user.role,
                            last_login=user.last_login.isoformat(),
                            api_token=user.api_token)
                data['profile'] = dict(first_name=user.profile.first_name,
                                       last_name=user.profile.last_name)

            # Otherwise, set error message
            else:
                request.response.status = '422 Unprocessable Entity'
                errors['_global'] = 'Invalid email or password.'

        return dict(data=data, errors=errors)

    @action(renderer='json')
    @validate(UserRegisterForm, allow_json=True)
    def register(self):
        """
        Register a user.

        :returns: A JSON object containing:

            :data:    An object reflecting the registered user.
            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/register email=email@example.com password=secret confirm=secret profile:='{"first_name": "John", "last_name": "Smith"}'

        Example response:

        .. code-block:: json

            {
                "data": {
                    "api_token": "1a2b3c4d5e",
                    "email": "email@example.com",
                    "id": 1,
                    "last_login": "2014-10-23T17:50:08.053533",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user"
                },
                "errors": {}
            }
        """
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.POST
        errors = self.validation_errors
        data = None

        # Check and process form submission
        if errors:
            request.response.status = '422 Unprocessable Entity'
        else:
            try:
                user = User(email=params['email'], password=params['password'])
                user.last_login = datetime.utcnow()
                user.profile = UserProfile(**params['profile'])

                DBSession.add(user)
                DBSession.flush()
            except Exception as exc:
                if 'unique' in str(exc).lower():
                    errors['email'] = 'Email address is already registered'
                    request.response.status = '422 Unprocessable Entity'
                else:
                    errors['_global'] = 'Unable to process register'
                    logger.error('Failed to register user: %s' % exc)
                    request.response.status = '500 Internal Server Error'
            else:
                data = dict(id=user.id, email=user.email, role=user.role,
                            last_login=user.last_login.isoformat(),
                            api_token=user.api_token)
                data['profile'] = dict(first_name=user.profile.first_name,
                                       last_name=user.profile.last_name)

        return dict(data=data, errors=errors)

    @action(renderer='json')
    @validate(validators=dict(email=Email(not_empty=True)), allow_json=True)
    def forgot_password(self):
        """
        Send "forgot password" email for user.

        :returns: A JSON object containing:

            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/forgot_password email=email@example.com

        Example response::

            HTTP/1.1 200 OK
        """
        # Initialize request variables
        request = self.request
        params = self.validation_results or request.POST
        errors = self.validation_errors

        # Check and process form submission
        if errors:
            request.response.status = '422 Unprocessable Entity'
        else:
            try:
                user = User.by_email(params['email'])
                user.password_reset_token = generate_secret()
                user.password_reset_sent = datetime.utcnow()
            except:
                errors['_global'] = 'Invalid email address.'
                request.response.status = '422 Unprocessable Entity'
            else:
                # Prep email
                link = request.route_url(
                    'users',
                    action='reset_password',
                    _query=dict(email=user.email,
                                token=user.password_reset_token)
                )
                html = render('emails/forgot_password.jinja2', dict(link=link))
                text = html2text(html)

                # Send email
                mailer = get_mailer(request)
                message = Message(subject='Starter Password Reset',
                                  recipients=[user.email],
                                  sender='info@example.com',
                                  body=text, html=html)
                mailer.send(message)

        return dict(data=None, errors=errors)

    @action(renderer='json')
    @validate(UserResetPasswordForm, allow_json=True)
    def reset_password(self):
        """
        Reset user's password.

        :returns: A JSON object containing:

            :errors: ``null`` if no error was encountered, otherwise an object
                     containing the error message(s).

        Example request::

            http -j POST :/api/users/reset_password token=1a2b3c4d5e email=email@example.com password=123456 confirm=123456

        Example response::

            HTTP/1.1 200 OK
        """
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.POST
        errors = self.validation_errors

        if errors:
            request.response.status = '422 Unprocessable Entity'
        elif params:
            try:
                a_week_ago = datetime.utcnow() - timedelta(days=7)

                user = User.query.filter(
                    User.email == params['email'],
                    User.password_reset_token == params['token'],
                    User.password_reset_sent >= a_week_ago
                ).one()
            except:
                request.response.status = '422 Unprocessable Entity'
                errors['_global'] = 'Could not verify reset parameters.'
            else:
                user.password = params['password']
                user.password_reset_token = None

        return dict(data=None, errors=errors)
