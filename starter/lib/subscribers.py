"""
Subscribers
-----------
"""
# System imports
import logging
import subprocess
from os import path

# App imports
from . import helpers
from .auth import get_token_credentials
from ..models import User

def before_renderer(event):
    """Perform renderer globals injection."""
    event['h'] = helpers

def get_current_user(request):
    """Get the current user object."""
    userid = request.unauthenticated_userid

    if userid:
        if request.headers.get('Authorization'):
            # We're using Token Authentication
            credentials = get_token_credentials(request)

            if credentials:
                return User.first(User.email == userid,
                                  User.api_token == credentials['token'])
        else:
            # We're using AuthTkt Authentication
            return User.first(User.email == userid)

    return None
