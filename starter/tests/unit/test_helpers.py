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