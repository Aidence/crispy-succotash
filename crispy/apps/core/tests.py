from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase


class BaseTestCase(TestCase):
    factory = RequestFactory()

    def _test_view_for_status_code(self, view_name, url_kwargs={}, status_code=200):
        response = self.client.get(reverse(view_name, kwargs=url_kwargs))
        self.assertEqual(response.status_code, status_code)
