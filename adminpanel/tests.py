from django.test import TestCase
from .models import *


class TestingAppModels(TestCase):
    def test_model_str(self):
        title = Category.objects.create(category_name='testing tests.py')
        self.assertEqual(str(title.category_name), "testing tests.py")
