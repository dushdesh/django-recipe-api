from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """Test publicly avaialble tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_for_tag_list(self):
        """Test that login is required to access tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_for_create_tag(self):
        """Test that login is required to create tags"""
        res = self.client.post(TAGS_URL, {'name': 'Indian'})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test tags API for authorized user"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='gandalf@lotr.com',
            password='youShallNotPass',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Chinese')
        Tag.objects.create(user=self.user, name='Indian')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that the tags retrieved belogn to the authenticated user"""
        new_user = get_user_model().objects.create_user(
            email='samwise@lotr.com',
            password='mrfrodo',
        )
        Tag.objects.create(user=new_user, name='Chinese')
        tag = Tag.objects.create(user=self.user, name='Indian')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_success(self):
        """Test creating a new tag is successful"""
        payload = {'name': 'Indian'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_invalid_tag_fail(self):
        """Test creating an invalid tag fails"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
