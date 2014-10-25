"""
Starter routes.

TBD
"""
from .views import *

# Register routes
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html#route-configuration
def includeme(config):
    # System routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_forbidden_view(forbidden) # .views.forbidden

    # Root - /

    # GET / -> root:Root.index
    config.add_handler('root_index',
                       pattern='',
                       handler=Root,
                       action='index',
                       request_method='GET')
    # Handler: /{action}.html -> root:Root.{action}
    config.add_handler('root',
                       pattern='/{action}.html',
                       handler=Root)

    # Users - /users/

    # Handler: /users/{action}.html -> users:Users.{action}
    config.add_handler('users',
                       pattern='/users/{action}.html',
                       handler=Users)

    # Admin - /admin/

    # GET /admin/ -> admin.root:AdminRoot.index
    config.add_handler('admin_index',
                       pattern='/admin/',
                       handler=AdminRoot,
                       action='index',
                       request_method='GET')
    # Handler: /admin/{action}.html -> admin.root:AdminRoot.{action}
    config.add_handler('admin',
                       pattern='/admin/{action}.html',
                       handler=AdminRoot)

    # API - /api/*

    # GET /api/ -> api.root:APIRoot.index
    config.add_handler('api_index',
                       pattern='/api/',
                       handler=APIRoot,
                       action='index',
                       request_method='GET',
                       header='Accept:application/json')
    # GET /api/users[.json|/] -> api.users:APIUsers.index
    config.add_handler('api_users_index',
                       pattern='/api/users{_:(\.json|/)?}',
                       handler=APIUsers,
                       action='index',
                       request_method='GET',
                       header='Accept:application/json')
    # POST /api/users[.json|/] -> api.users:APIUsers.create
    config.add_handler('api_users_create',
                       pattern='/api/users{_:(\.json|/)?}',
                       handler=APIUsers,
                       action='create',
                       request_method='POST',
                       header='Accept:application/json')
    # GET /api/users/:id[.json] -> api.users:APIUsers.read
    config.add_handler('api_users_read',
                       pattern='/api/users/{id:\d+}{_:(\.json)?}',
                       handler=APIUsers,
                       action='read',
                       request_method='GET',
                       header='Accept:application/json')
    # PATCH/PUT/POST /api/users/:id[.json] -> api.users:APIUsers.update
    config.add_handler('api_users_update',
                       pattern='/api/users/{id:\d+}{_:(\.json)?}',
                       handler=APIUsers,
                       action='update',
                       request_method=('PATCH', 'PUT', 'POST'),
                       header='Accept:application/json')
    # DELETE /api/users/:id[.json] -> api.users:APIUsers.delete
    config.add_handler('api_users_delete',
                       pattern='/api/users/{id:\d+}{_:(\.json)?}',
                       handler=APIUsers,
                       action='delete',
                       request_method=('DELETE'),
                       header='Accept:application/json')

    # POST /api/users/login[.json] -> api.users:APIUsers.login
    config.add_handler('api_users_login',
                       pattern='/api/users/login{_:(\.json)?}',
                       handler=APIUsers,
                       action='login',
                       request_method='POST',
                       header='Accept:application/json')
    # POST /api/users/register[.json] -> api.users:APIUsers.register
    config.add_handler('api_users_register',
                       pattern='/api/users/register{_:(\.json)?}',
                       handler=APIUsers,
                       action='register',
                       request_method='POST',
                       header='Accept:application/json')
    # POST /api/users/forgot_password[.json]
    # -> api.users:APIUsers.forgot_password
    config.add_handler('api_users_forgot_password',
                       pattern='/api/users/forgot_password{_:(\.json)?}',
                       handler=APIUsers,
                       action='forgot_password',
                       request_method='POST',
                       header='Accept:application/json')
    # POST /api/users/reset_password[.json]
    # -> api.users:APIUsers.reset_password
    config.add_handler('api_users_reset_password',
                       pattern='/api/users/reset_password{_:(\.json)?}',
                       handler=APIUsers,
                       action='reset_password',
                       request_method='POST',
                       header='Accept:application/json')

    # OPTIONS /api/* -> api:APIView.options
    config.add_handler('api_options',
                       pattern='/api/*_',
                       handler=APIRoot,
                       action='options',
                       request_method='OPTIONS')

    # Handler: /api/{action}.json -> api.root:APIRoot.{action}
    config.add_handler('api_handler',
                       pattern='/api/{action}.json',
                       handler=APIRoot,
                       header='Accept:application/json')
