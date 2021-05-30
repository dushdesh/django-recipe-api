from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdmimSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@dushdesh.com",
            password="admin123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@dushdesh.com",
            password="test123",
            name="Test User"
        )

    def test_users_listed(self):
        # Test that users are listed on users page
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_edit_page(self):
        # Test user edit page works
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        # Test that the user create page works
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
