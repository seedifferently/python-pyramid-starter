"""
Form Validation
---------------
"""
# System imports
from functools import wraps

# 3rd party imports
from formencode.api import Invalid
from formencode.schema import Schema
from formencode.variabledecode import NestedVariables
from formencode.validators import FieldsMatch, UnicodeString, Int, Email, OneOf

# Pyramid imports
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPBadRequest


# Give formencode's "Invalid" class a __json__ method
Invalid.__json__ = lambda obj, request: str(obj)


# User schema validators
class UserCreateSchema(Schema):
    """Schema for User create (fields may not be missing)."""
    email = Email(max=255, not_empty=True)
    password = UnicodeString(min=6)
    role = OneOf(('user', 'superuser', 'admin'), if_missing='user',
                         hideList=True)

    class profile(Schema):
        first_name = UnicodeString(max=100, not_empty=True)
        last_name = UnicodeString(max=100, not_empty=True)

class UserUpdateSchema(Schema):
    """Schema for User update (fields may be missing)."""
    ignore_key_missing = True

    email = Email(max=255, not_empty=True)
    password = UnicodeString(min=6)
    role = OneOf(('user', 'superuser', 'admin'), hideList=True, not_empty=True)

    class profile(Schema):
        first_name = UnicodeString(max=100, not_empty=True)
        last_name = UnicodeString(max=100, not_empty=True)

# User form validators
class UserLoginForm(Schema):
    """Schema for User login form."""
    email = Email(not_empty=True)
    password = UnicodeString(not_empty=True)
    next = UnicodeString(if_missing=None)

class UserRegisterForm(Schema):
    """Schema for User register form."""
    pre_validators = [NestedVariables]
    chained_validators = [FieldsMatch('password', 'confirm')]

    email = Email(max=255, not_empty=True)
    password = UnicodeString(min=6)
    confirm = UnicodeString(not_empty=True)

    class profile(Schema):
        first_name = UnicodeString(max=100, not_empty=True)
        last_name = UnicodeString(max=100, not_empty=True)

class UserResetPasswordForm(Schema):
    """Schema for User password reset form."""
    chained_validators = [FieldsMatch('password', 'confirm')]

    email = Email(not_empty=True)
    password = UnicodeString(min=6)
    confirm = UnicodeString(not_empty=True)
    token = UnicodeString(not_empty=True)


# @validate decorator, adapted from Pylons
class validate(object):
    """
    Validate input either for a FormEncode schema, or individuallly specified
    validators.

    Given a form schema or a dict of validators, @validate will attempt to
    validate the schema or validator dict. If validation is successful, the
    validated results will be saved to a ``self.validation_results`` dict.
    Otherwise, the action will be re-run as if it was a GET request, and any
    errors will be saved to ``self.validation_errors``.

    ``schema``
        Refers to a FormEncode Schema object to use during validation.
    ``validators``
        A dict of param "keys" and formencode "values" to validate.
    ``methods``
        A list of request methods to process (defaults to ['POST']). If the
        current request method is not in this list then no validation will be
        performed.

        Currently only GET and POST are supported.

        .. warning::
            This parameter also determines where submitted data is read from.
            If using the default (['POST']), then data will only be read
            from request.POST. If ['POST', 'GET'] is used, then data will be
            read from request.mixed, etc.
    ``state``
        Passed through to FormEncode for use in validators that utilize a state
        object.
    ``verify_csrf``
        Whether to verify CSRF token via Pyramid's ``session.check_csrf_token``
        method (POST requests only--defaults to True).
    ``allow_json``
        Whether to parse submitted data from ``request.json`` if the request
        content-type matches "application/json"

        .. warning::
            If ``allow_json`` is True, ``verify_csrf`` is automatically set to
            False when parsing JSON data, which could open your app up to CSRF
            attacks if you aren't verifying identity via other means (e.g. API
            token verification).

    .. note::
        This specific flavor of the @validate decorator is meant to be used with
        ``pyramid_handlers`` view class actions.

        Example::

            class HandlerClass(object):
                def __init__(self, request):
                    self.request = request

                @action(renderer='login.tmpl')
                @validate(forms.LoginFormSchema, methods=['GET', 'POST'])
                def login(self):
                    # Do something with ``self.validation_results``, or display
                    # ``self.validation_errors``
    """
    def __init__(self, schema=None, validators=None, methods=['POST'],
                 state=None, verify_csrf=True, allow_json=False):
        self.schema = schema
        self.validators = validators
        self.methods = [x.upper() for x in methods \
                        if x.upper() in ['GET', 'POST']]
        self.state = state
        self.verify_csrf = verify_csrf
        self.allow_json = allow_json

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(cls):
            request = cls.request
            errors = cls.validation_errors = dict()
            cls.validation_results = dict()

            if request.method.upper() in self.methods:
                if self.allow_json and \
                   request.content_type.startswith('application/json'):
                    # Parse JSON body instead of HTTP POST vars
                    try:
                        params = request.json
                    except:
                        raise HTTPBadRequest
                    else:
                        # Don't verify CSRF for JSON requests, as Auth headers
                        # should always be sent.
                        self.verify_csrf = False
                elif len(self.methods) > 1:
                    params = request.params.mixed()
                else:
                    params = getattr(request, self.methods[0])

                # Validate CSRF
                if self.verify_csrf and request.method.upper() == 'POST':
                    check_csrf_token(request)
                    del params['csrf_token']

                # Validate Schema
                if self.schema:
                    try:
                        cls.validation_results = self.schema.to_python(
                            params,
                            self.state
                        )
                    except Invalid as err:
                        if NestedVariables in getattr(self.schema,
                                                      'pre_validators', []):
                            try:
                                errors = err.unpack_errors(True)
                            except:
                                errors = err.unpack_errors(False)
                        else:
                            errors = err.unpack_errors(False)

                # Validate Validators
                if self.validators:
                    for field, validator in self.validators.items():
                        try:
                            cls.validation_results[field] = \
                                validator.to_python(params.get(field),
                                                    self.state)
                        except Invalid as err:
                            errors[field] = err

                if errors:
                    cls.validation_errors = errors if isinstance(errors, dict) \
                                                   else dict(_global=errors)

            return fn(cls)

        return wrapper
