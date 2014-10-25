"""
Users View (/users/)
--------------------
"""
# System imports
from datetime import datetime, timedelta
import logging

# 3rd party imports
from html2text import html2text

# Pyramid imports
from pyramid.renderers import render
from pyramid.security import authenticated_userid, remember, forget
from pyramid.httpexceptions import HTTPFound
from pyramid.session import check_csrf_token
from pyramid_handlers import action
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

# Project imports
from . import View
from ..lib.validation import (validate, Email, UserLoginForm, UserRegisterForm,
                              UserResetPasswordForm)
from ..lib.helpers import set_secure_cookie, generate_secret
from ..models import DBSession, User, UserProfile


logger = logging.getLogger(__name__)


class Users(View):
    """
    The "Users" view handler class.

    Responsible for requests to the ``/users/`` routes.
    """

    @action(renderer='users/login.jinja2')
    @validate(UserLoginForm, methods=['GET', 'POST'])
    def login(self):
        """``/users/login.html``"""
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.params
        errors = self.validation_errors

        # Set up response variables
        next = params.get('next') or request.route_path('root_index')
        email = params.get('email')
        password = params.get('password')

        # If the current user is already logged in, redirect to root
        if authenticated_userid(request):
            flash(('You are already logged in.', 'info'))
            return HTTPFound(location=next)

        # Check and process form submission
        if errors:
            if params.get('email') or params.get('password'):
                flash(('Invalid email or password.', 'danger'))
        else:
            # If user validates, set header and redirect
            user = User.filter_by(email=email).first()

            if user and user.check_password(password):
                # Update last login timestamp
                user.last_login = datetime.utcnow()

                # Prepare the response
                headers = remember(request, email)
                response = HTTPFound(location=next, headers=headers)

                # Store email cookie (for future logins) for 30 days
                set_secure_cookie(response, 'email', email, max_age=2592000)

                return response

            # Otherwise, set error message
            flash(('Invalid email or password.', 'danger'))

        return dict(email=email, next=next)

    @action(renderer=None)
    def logout(self):
        """``/users/logout.html``"""
        # Initialize request variables
        request = self.request
        flash = request.session.flash

        request.session.invalidate()
        flash(('You have successfully logged out.', 'info'))
        headers = forget(request)

        return HTTPFound(location=request.route_path('root_index'),
                         headers=headers)

    @action(renderer='users/register.jinja2')
    @validate(UserRegisterForm)
    def register(self):
        """``/users/register.html``"""
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.POST
        errors = self.validation_errors

        # If the current user is already logged in, redirect to root
        if authenticated_userid(request):
            flash(('You are already logged in.', 'info'))
            return HTTPFound(location=request.route_url('root_index'))

        if errors:
            flash(('Please correct the specified errors.', 'danger'))
        elif params:
            try:
                user = User(email=params['email'], password=params['password'])
                user.profile = UserProfile(**params['profile'])

                DBSession.add(user)
                DBSession.flush()
            except Exception as exc:
                if 'unique' in str(exc).lower():
                    errors['email'] = 'Email address is already registered'
                else:
                    flash(('Unable to process registration.', 'danger'))
                    logger.error('Failed to register user: %s' % exc)

                # Make sure un-nested params are returned to the template
                params = request.POST
            else:
                # If user validates, log in and redirect
                headers = remember(request, user.email)

                return HTTPFound(location=request.route_url('root_index'),
                                 headers=headers)


        return dict(params=params, errors=errors)

    @action(renderer='users/forgot_password.jinja2')
    @validate(validators=dict(email=Email(not_empty=True)))
    def forgot_password(self):
        """``/users/forgot_password.html``"""
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.POST
        errors = self.validation_errors

        if errors:
            flash(('Please correct the specified errors.', 'danger'))
        elif params:
            try:
                user = User.by_email(params['email'])
                user.password_reset_token = generate_secret()
                user.password_reset_sent = datetime.utcnow()
            except:
                flash(('Invalid email address.', 'danger'))
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

                flash(('Password reset link has been emailed to you.', 'info'))

        return dict(params=params)

    @action(renderer='users/reset_password.jinja2')
    @validate(UserResetPasswordForm)
    def reset_password(self):
        """``/users/reset_password.html``"""
        # Initialize request variables
        request = self.request
        flash = request.session.flash
        params = self.validation_results or request.params
        errors = self.validation_errors

        if errors:
            flash(('Please correct the specified errors.', 'danger'))
        elif params and request.POST:
            try:
                a_week_ago = datetime.utcnow() - timedelta(days=7)

                user = User.query.filter(
                    User.email == params['email'],
                    User.password_reset_token == params['token'],
                    User.password_reset_sent >= a_week_ago
                ).one()
            except:
                flash(('Could not verify reset parameters.', 'danger'))
            else:
                user.password = params['password']
                user.password_reset_token = None

                flash('Your password was successfully changed.')

                return HTTPFound(
                    location=request.route_url('users', action='login')
                )
        return dict(params=params, errors=errors)

    @action(renderer='users/me.jinja2', permission='user_permissions')
    def me(self):
        """``/users/me.html``"""
        # Initialize request variables
        request = self.request

        return dict(user=request.current_user)
