"""
Admin Root View (/admin/)
-------------------------
"""
# Pyramid imports
from pyramid_handlers import action

# Project imports
from . import AdminView

class AdminRoot(AdminView):
    """
    The "AdminRoot" view handler class.

    Responsible for requests to the ``/admin/`` routes.
    """

    @action(renderer='admin/index.jinja2')
    def index(self):
        """``/admin/``"""
        return dict()
