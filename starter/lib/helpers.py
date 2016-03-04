"""
Helpers
-------
"""
# System imports
import os
import string
import binascii

# 3rd party imports
from webhelpers2.html.builder import HTML
from webhelpers2.html.tags import link_to, image

# Pyramid imports
from pyramid.compat import native_
from pyramid.session import signed_serialize, signed_deserialize

# Project imports
from .settings import SETTINGS

def set_secure_cookie(response, key, value, **kw):
    """Sets a secure/signed cookie."""
    signed_value = signed_serialize(value, SETTINGS['cookie.secret'])

    response.set_cookie(key, signed_value, **kw)

def get_secure_cookie(request, key):
    """Gets the value of a secure/signed cookie."""
    signed_value = request.cookies.get(key)

    if signed_value:
        try:
            return signed_deserialize(signed_value, SETTINGS['cookie.secret'])
        except:
            pass

def generate_secret(length=40):
    """
    Returns a random ascii hash of the specified length (default is 40).

    .. note:: Due to the way the secret is generated, ``length`` should always
              be an even number.
    """
    return native_(binascii.hexlify(os.urandom(int(length / 2))))