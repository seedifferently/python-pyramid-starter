from pyramid.security import ACLAllowed
from pyramid.httpexceptions import HTTPForbidden
from .. import View

# Define the master AdminView class
class AdminView(View):
    def __init__(self, request):
        super(AdminView, self).__init__(request)

        if not isinstance(request.has_permission('admin_permissions',
                                                 request.context), ACLAllowed):
            raise HTTPForbidden
