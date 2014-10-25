"""
Helpers
-------
"""
# System imports
import os
import string
import binascii

# 3rd party imports
from webhelpers2.html.builder import HTML
from webhelpers2.html.tags import link_to, image, form, end_form, text, select

# Pyramid imports
from pyramid.compat import native_
from pyramid.session import signed_serialize, signed_deserialize

# Project imports
from .settings import SETTINGS

def set_secure_cookie(response, key, value, **kw):
    """Sets a secure/signed cookie."""
    signed_value = signed_serialize(value, SETTINGS['cookie.secret'])

    response.set_cookie(key, signed_value, **kw)

def get_secure_cookie(request, key):
    """Gets the value of a secure/signed cookie."""
    signed_value = request.cookies.get(key)

    if signed_value:
        try:
            return signed_deserialize(signed_value, SETTINGS['cookie.secret'])
        except:
            pass

def generate_secret(length=40):
    """
    Returns a random ascii hash of the specified length (default is 40).

    .. note:: Due to the way the secret is generated, ``length`` should always
              be an even number.
    """
    return native_(binascii.hexlify(os.urandom(int(length / 2))))

def horizontal_form_input(name, value=None, errors={}, type='text',
                          label_text=None, help_text=None, error_text=None,
                          required=False, label_kw={},
                          grid_classes=['col-sm-2', 'col-sm-10 col-md-8'],
                          **kw):
    """
    Form <input> helper which uses twitter-bootstrap 3 friendly markup.

    By default the label text is extracted from the input name. Set label_text
    to False if you do not want a label element to be included in your output.
    """
    # Set container class
    container_class = 'form-group'
    container_class += ' has-error' if error_text or errors.get(name) else ''

    # Set control class
    kw['id'] = kw.get('id') or name.replace('.', '_')
    kw['class_'] = 'form-control %s' % kw.get('class_', '')

    if type == 'select':
        control_content = select(name, value, **kw)
    else:
        # Set required
        if required:
            kw['required'] = 'required'
        # Set placeholder
        if kw.get('placeholder') == False:
            del kw['placeholder']
        else:
            kw['placeholder'] = kw.get('placeholder') or \
                                label_kw.get('title') or \
                                label_text or \
                                name.split('.')[-1].replace('_', ' ').title()

        control_content = text(name, value, type=type, **kw)

    if error_text or errors.get(name):
        control_content += HTML.span(error_text or errors.get(name),
                                     class_='help-block')
    if help_text:
        control_content += HTML.span(help_text, class_='help-block')

    if label_text == False:
        return HTML.div(
            HTML.div(
                control_content,
                class_='controls'
            ),
            class_= container_class
        )
    else:
        label_text = label_text or name.split('.')[-1].replace('_', ' ').title()
        label_class = 'control-label ' + grid_classes[0]
        label_class += ' required' if required else ''

        return HTML.div(
            HTML.label(label_text, for_=name, class_=label_class, **label_kw) +
            HTML.div(
                control_content,
                class_=grid_classes[1]
            ),
            class_= container_class
        )

def horizontal_form_submit(submit_text='Submit',
                           button_class='btn btn-default',
                           grid_class='col-sm-offset-2 col-sm-10',
                           **kw):
    """
    A <button type="submit"> helper which uses twitter-bootstrap 3 friendly
    markup.
    """
    return HTML.div(
        HTML.div(
            HTML.button(submit_text, type='submit', class_=button_class,
                        **kw),
            class_=grid_class
        ),
        class_= 'form-group'
    )
