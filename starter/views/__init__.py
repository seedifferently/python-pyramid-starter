"""
Views Module
------------
"""
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..lib.auth import __acl__


__all__ = ['View', 'forbidden', 'Root', 'Users', 'AdminRoot', 'APIRoot',
           'APIUsers']

class View(object):
    """
    The master View class for the app.

    .. note:: Pagination size is handled via the ``items_per_page`` attribute.
    """
    def __init__(self, request):
        self.request = request
        self.items_per_page = 25
        self.__acl__ = __acl__

def forbidden(request):
    """
    The custom ``forbidden`` view.

    By customizing the ``forbidden`` view, we can do things like redirect
    unauthenticated users to the login page, or return a proper JSON forbidden
    response.
    """
    flash = request.session.flash
    next = request.current_route_path()

    # If accepting JSON, just respond with a 401 or 403
    if 'application/json' in str(request.accept):
        # Prepare the JSON response object
        response = Response(content_type='application/json')
        # This is a publicly accessible API
        response.headers.update({'Access-Control-Allow-Origin': '*'})

        # Set the appropriate response status
        if request.current_user:
            response.status = '403 Forbidden'
        else:
            response.status = '401 Unauthorized'
            # Token authorization is expected
            response.headers.update({'WWW-Authenticate': 'Token'})

        return response
    # Otherwise, return a redirect
    elif request.current_user:
        flash(('You are not authorized to access that location.', 'warning'))
        return HTTPFound(location=request.route_path('root_index'))
    else:
        flash(('Please log in before continuing.', 'warning'))
        return HTTPFound(
            location=request.route_path('users', action='login',
                                        _query=dict(next=next))
        )


# Load view classes
from .root import Root
from .users import Users
from .admin.root import AdminRoot
from .api.root import APIRoot
from .api.users import APIUsers
