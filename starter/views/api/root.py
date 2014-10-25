"""
API Root View (/api/)
---------------------
"""
# Pyramid imports
from pyramid_handlers import action

# Project imports
from . import APIView
from starter.models import User


class APIRoot(APIView):
    """
    The "APIRoot" view handler class.

    Responsible for JSON requests to the ``/api/`` routes.
    """
    @action(renderer='json')
    def index(self):
        """
        API root index.

        Example request::

            http -j :/api/

        Example response:

        .. code-block:: json

            {
                "data": "data"
            }
        """
        return dict(data='data')

    @action(renderer='json')
    def me(self):
        """
        Show information about the current user.

        :returns: A JSON object containing:

            :data: A ``User`` object reflecting the current user (or ``null``
                   if none).

        Example request::

            http -j :/api/me.json Authorization:"Token ..."

        Example response:

        .. code-block:: json

            {
                "data": {
                    "created": "2014-09-23T09:38:25.131009+00:00",
                    "email": "email@example.com",
                    "id": 1,
                    "last_login": "2014-09-23T09:41:25.131009+00:00",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Smith"
                    },
                    "role": "user",
                    "updated": "2014-09-23T09:38:25.130992+00:00"
                }
            }
        """
        return dict(data=self.request.current_user)
