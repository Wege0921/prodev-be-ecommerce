from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', is_admin=True)
        self.client.login(username='admin', password='pass')  # or use JWT token
        self.cat = Category.objects.create(name='Electronics')
        Product.objects.create(title='Phone', price=499.99, category=self.cat, stock=5)

    def test_list_products(self):
        url = reverse('product-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.data['results']), 0)

    def test_filter_by_category(self):
        url = reverse('product-list') + f'?category={self.cat.id}'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(all(item['category']['id'] == self.cat.id for item in res.data['results']))
