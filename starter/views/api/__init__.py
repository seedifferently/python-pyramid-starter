"""
Each API call requires the ``Accept`` HTTP header to be set to
``application/json``.

User authentication is achieved by sending an "``Authorization: Token ...``"
HTTP header with the request.

To compute the authorization token, join the user's ``email`` and ``api_token``
strings with a colon and base64 encode the result. For example, if the user's
email is ``user@example.com`` and their API token is ``1a2b3c4d5e``, then the
auth token would be the base64 value of "``user@example.com:1a2b3c4d5e``",
resulting in an ``Authorization`` header of::

    Authorization: Token dXNlckBleGFtcGxlLmNvbToxYTJiM2M0ZDVl

Most JSON responses will have an ``errors`` object that will be ``null`` unless
an error was encountered, in which case it will contain the error message(s).

.. note:: Example requests are shown using `HTTPie <http://httpie.org>`_ (a
          user-friendly cURL replacement).
"""
# Pyramid imports
from pyramid_handlers import action

# Project imports
from starter.lib.auth import __acl__
from starter.views import View

# Define the master APIView class
class APIView(View):
    """
    :Version: X.X
    :Last Updated: XX/XX/XXXX
    """
    def __init__(self, request):
        super(APIView, self).__init__(request)

        # Paginate 100 items on API requests
        self.items_per_page = 100

        # This is a publicly accessible API
        request.response.headers.update({
            'Access-Control-Allow-Origin': '*'
        })

    @action()
    def options(self):
        """
        Preflight check.
        """
        # Initialize request variables
        request = self.request

        # Initialize response
        request.response.status = '204 No Content'
        request.response.headers.update({
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE',
            'Access-Control-Allow-Headers':
                'Accept, Authorization, Content-Type, Content-Language, '
                'Last-Modified, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '86400'
        })

        return request.response
