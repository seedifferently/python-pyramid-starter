# System imports
from os import path

# 3rd party imports
from sqlalchemy import engine_from_config

# Pyramid imports
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory
from pyramid.events import ApplicationCreated, NewRequest, BeforeRender
from pyramid_jinja2 import renderer_factory

# App imports
from .lib.subscribers import before_renderer, get_current_user
from .lib.auth import TokenOrAuthTktAuthenticationPolicy, get_role
from .lib.settings import SETTINGS
from .models import DBSession, Base
from .views import View
from . import routes


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # Update settings dict
    SETTINGS.update(settings)

    # Initialize database session
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # Initialize session
    session_factory = SignedCookieSessionFactory(
        settings['session.secret'],
        cookie_name=settings['session.cookie_name'],
        timeout=7200,
        reissue_time=300
    )

    # Initialize auth
    authn_policy = TokenOrAuthTktAuthenticationPolicy(
        settings['auth.secret'],
        callback=get_role,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()

    # Build config
    config = Configurator(
        root_factory=View, # .views.View
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory,
    )

    # config.add_translation_dirs('locale/')

    # Run injectors/subscribers
    # request.environment -- current env
    config.add_request_method(
        lambda req: path.basename(path.splitext(global_config['__file__'])[0]),
        name='environment',
        reify=True
    )
    # request.current_user -- current user (if logged in)
    config.add_request_method(get_current_user, 'current_user', reify=True)
    # .lib.subscribers.before_renderer
    config.add_subscriber(before_renderer, BeforeRender)

    # Run package includes
    config.include('pyramid_tm')
    config.include('pyramid_handlers')
    config.include('pyramid_jinja2')

    # Register routes
    config.include(routes)

    # Scan for and run any extra configs
    # config.scan(ignore='.tests')

    return config.make_wsgi_app()
