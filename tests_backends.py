"""Tests for the custom authentication backend."""
import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

from django.contrib.auth.models import User
from django.test import TestCase

from backends import CaseInsensitiveModelBackend


class CaseInsensitiveBackendTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser', password='correctpassword'
        )
        self.backend = CaseInsensitiveModelBackend()

    def test_authenticate_exact_case(self):
        result = self.backend.authenticate(request=None, username='TestUser', password='correctpassword')
        self.assertEqual(result, self.user)

    def test_authenticate_lowercase(self):
        result = self.backend.authenticate(request=None, username='testuser', password='correctpassword')
        self.assertEqual(result, self.user)

    def test_authenticate_uppercase(self):
        result = self.backend.authenticate(request=None, username='TESTUSER', password='correctpassword')
        self.assertEqual(result, self.user)

    def test_authenticate_wrong_password(self):
        result = self.backend.authenticate(request=None, username='TestUser', password='wrongpassword')
        self.assertIsNone(result)

    def test_authenticate_nonexistent_user(self):
        result = self.backend.authenticate(request=None, username='nobody', password='anything')
        self.assertIsNone(result)
