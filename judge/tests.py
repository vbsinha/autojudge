from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class IndexViewTests(TestCase):
    def test_no_contests_index_view(self):
        response = self.client.get(reverse('judge:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no contests")
        self.assertQuerysetEqual(response.context['contests'], [])
