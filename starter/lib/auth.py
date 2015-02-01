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

    try:
        authmeth, auth = authorization.split(' ', 1)
    except:
        return None
    else:
        # Normalize "authmeth"
        authmeth = authmeth.lower()
        # Make sure "auth" doesn't have any unwanted whitespace
        auth = auth.strip()

    if authmeth == 'token':
        # Parse traditional token value
        try:
            authbytes = b64decode(auth)
        except (TypeError, binascii.Error): # can't decode
            return None

        # Try utf-8 first, then latin-1; see discussion in
        # https://github.com/Pylons/pyramid/issues/898
        try:
            auth = authbytes.decode('utf-8')
        except UnicodeDecodeError:
            auth = authbytes.decode('latin-1')

        try:
            userid, token = auth.split(':', 1)
        except ValueError: # not enough values to unpack
            return None

        return dict(userid=userid, token=token)

    return None

class TokenOrAuthTktAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """AuthenticationPolicy for either an API token, or AuthTkt cookie."""
    def unauthenticated_userid(self, request):
        if request.headers.get('Authorization'):
            # Check for the userid within the ``Authorization`` request header
            credentials = get_token_credentials(request)

            if credentials:
                return credentials['userid']
        else:
            # Check for the userid within the ``auth_tkt`` cookie
            credentials = self.cookie.identify(request)

            if credentials:
                return credentials['userid']
