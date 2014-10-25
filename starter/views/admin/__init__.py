from pyramid.security import ACLAllowed, has_permission
from pyramid.httpexceptions import HTTPForbidden
from starter.lib.auth import __acl__
from .. import View

# Define the master AdminView class
class AdminView(View):
    def __init__(self, request):
        super(AdminView, self).__init__(request)

        if not isinstance(has_permission('admin_permissions', request.context,
                                         request),
                          ACLAllowed):
            raise HTTPForbidden
