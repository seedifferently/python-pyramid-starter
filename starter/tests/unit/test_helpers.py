import re
from unittest import TestCase
from starter.lib.helpers import *


class HelpersUnitTest(TestCase):
    """Tests for the methods in the helpers lib."""

    def test_generate_secret(self):
        self.assertTrue(re.match(r'^[a-z0-9]{40}$', generate_secret()),
                        'Unspecified length secret check failed')
        self.assertTrue(re.match(r'^[a-zA-Z0-9]{10}$', generate_secret(10)),
                        'Specified length secret check failed')

    def test_horizontal_form_input(self):
        self.assertEqual(
            horizontal_form_input('name'),
            '<div class="form-group"><label class="control-label col-sm-2" ' +
            'for="name">Name</label><div class="col-sm-10 col-md-8"><input ' +
            'class="form-control " id="name" name="name" placeholder="Name" ' +
            'type="text" /></div></div>'
        )

        self.assertEqual(
            horizontal_form_input('name', type='select',
                                  options=[('first', 'first')]),
            '<div class="form-group"><label class="control-label col-sm-2" ' +
            'for="name">Name</label><div class="col-sm-10 col-md-8"><select ' +
            'class="form-control " id="name" name="name">\n<option value=' +
            '"first">first</option>\n</select></div></div>'
        )

    def test_horizontal_form_submit(self):
        self.assertEqual(
            horizontal_form_submit(),
            '<div class="form-group"><div class="col-sm-offset-2 col-sm-10">' +
            '<button class="btn btn-default" type="submit">Submit</button>' +
            '</div></div>'
        )
