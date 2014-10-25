"""
Root View (/)
-------------
"""
# Pyramid imports
from pyramid_handlers import action

# Project imports
from . import View


class Root(View):
    """
    The "Root" view handler class.

    Responsible for requests to the ``/`` (root) routes.
    """

    @action(renderer='index.jinja2')
    def index(self):
        """``/`` or ``/index.html``"""
        return dict()

    @action(renderer='about.jinja2')
    def about(self):
        """``/about.html``"""
        return dict()
