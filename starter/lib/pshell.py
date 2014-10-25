from webtest import TestApp

def setup(env):
    """Configuration helper for the ``pshell`` command."""
    env['request'].host = 'www.example.com'
    env['request'].scheme = 'http'
    env['testapp'] = TestApp(env['app'])
