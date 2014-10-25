"""
Auth
----
"""
# System imports
import binascii

# Pyramid imports
from pyramid.security import (authenticated_userid, Allowed, ACLAllowed, Allow,
                              Authenticated, ALL_PERMISSIONS, DENY_ALL)
from pyramid.authentication import AuthTktAuthenticationPolicy, b64decode

# Project imports
from ..models import User

# Define a basic role-based ACL
__acl__ = [
    (Allow, Authenticated, 'user_permissions'),
    (Allow, 'role:superuser', ('superuser_permissions', 'user_permissions')),
    (Allow, 'role:admin', ALL_PERMISSIONS),
    DENY_ALL
]

def get_role(userid, request):
    """Get the role based on the provided userid."""
    current_user = request.current_user

    if isinstance(current_user, User) and current_user.email == userid:
        return ['role:%s' % current_user.role]
    else:
        return None

def get_token_credentials(request):
    """Helper method for parsing API token credentials."""
    authorization = request.headers.get('Authorization')
    if not authorization:
        return None
    try:
        authmeth, auth = authorization.split(' ', 1)
    except ValueError: # not enough values to unpack
        return None
    if authmeth.lower() != 'token':
        return None

    try:
        authbytes = b64decode(auth.strip())
    except (TypeError, binascii.Error): # can't decode
        return None

    # try utf-8 first, then latin-1; see discussion in
    # https://github.com/Pylons/pyramid/issues/898
    try:
        auth = authbytes.decode('utf-8')
    except UnicodeDecodeError:
        auth = authbytes.decode('latin-1')

    try:
        userid, token = auth.split(':', 1)
    except ValueError: # not enough values to unpack
        return None
    return userid, token

class TokenOrAuthTktAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """AuthenticationPolicy for either an API token, or AuthTkt cookie."""
    def unauthenticated_userid(self, request):
        if request.headers.get('Authorization'):
            # Check for the userid within the ``Authorization`` request header
            credentials = get_token_credentials(request)

            if credentials:
                return credentials[0]
        else:
            # Check for the userid within the ``auth_tkt`` cookie
            credentials = self.cookie.identify(request)

            if credentials:
                return credentials['userid']
