from django.test import TestCase
from django.contrib.auth import get_user_model
from main.models import Category, Product, Customer, Cart, CartItem, Order, \
    OrderItem
from decimal import Decimal
import uuid

User = get_user_model()


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Электроника')
        cls.product = Product.objects.create(
            name='Смартфон X',
            description='Флагманский смартфон',
            price=Decimal('59990.00'),
            stock=10,
            category=cls.category
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Смартфон X')
        self.assertEqual(self.product.price, Decimal('59990.00'))
        self.assertEqual(self.product.stock, 10)

    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'Смартфон X')

    def test_product_stock_can_be_negative(self):
        self.product.stock = -5
        self.product.save()
        self.assertEqual(self.product.stock, -5)


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Электроника')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Электроника')

    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Электроника')


class CustomerModelTest(TestCase):
    """Тесты для модели Customer"""

    def setUp(self):
        self.unique_id = str(uuid.uuid4())[:8]
        self.username = f'test_customer_{self.unique_id}'
        # При создании пользователя автоматически создастся Customer через сигнал
        self.user = User.objects.create_user(
            username=self.username,
            password='testpass123',
            email=f'customer_{self.unique_id}@example.com'
        )
        # Получаем автоматически созданного Customer
        self.customer = self.user.customer
        # Обновляем его данные
        self.customer.phone = '1234567890'
        self.customer.country = 'Россия'
        self.customer.city = 'Москва'
        self.customer.street_address = 'ул. Тестовая, д. 1'
        self.customer.save()

    def tearDown(self):
        self.user.delete()

    def test_customer_creation(self):
        self.assertEqual(self.customer.user.username, self.username)
        self.assertEqual(self.customer.phone, '1234567890')

    def test_customer_full_address(self):
        expected = 'Россия, Москва, ул. Тестовая, д. 1'
        self.assertEqual(self.customer.full_address, expected)


class CartModelTest(TestCase):
    """Тесты для модели Cart"""

    def setUp(self):
        self.unique_id = str(uuid.uuid4())[:8]
        self.username = f'test_cart_{self.unique_id}'
        self.user = User.objects.create_user(username=self.username)
        # Получаем автоматически созданного Customer
        self.customer = self.user.customer
        self.customer.phone = '1234567890'
        self.customer.country = 'Россия'
        self.customer.city = 'Москва'
        self.customer.street_address = 'ул. Тестовая, д. 1'
        self.customer.save()

        self.cart = Cart.objects.create(customer=self.customer)

        self.category = Category.objects.create(name='Тест')
        self.product = Product.objects.create(
            name='Тестовый товар',
            price=Decimal('100.00'),
            stock=10,
            category=self.category
        )

    def tearDown(self):
        CartItem.objects.filter(cart=self.cart).delete()
        self.cart.delete()
        self.product.delete()
        self.category.delete()
        self.user.delete()

    def test_cart_creation(self):
        self.assertEqual(self.cart.customer.user.username, self.username)

    def test_cart_total_price_empty(self):
        self.assertEqual(self.cart.total_price, 0)

    def test_cart_total_price_with_item(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_price, Decimal('300.00'))

    def test_cart_total_quantity(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.assertEqual(self.cart.total_quantity, 3)


class OrderModelTest(TestCase):
    """Тесты для модели Order"""

    def setUp(self):
        self.unique_id = str(uuid.uuid4())[:8]
        self.username = f'test_order_{self.unique_id}'
        self.user = User.objects.create_user(username=self.username)
        # Получаем автоматически созданного Customer
        self.customer = self.user.customer
        self.customer.phone = '1234567890'
        self.customer.country = 'Россия'
        self.customer.city = 'Москва'
        self.customer.street_address = 'ул. Тестовая, д. 1'
        self.customer.save()

        self.order = Order.objects.create(
            customer=self.customer,
            total_price=Decimal('1000.00'),
            status='new'
        )

    def tearDown(self):
        self.order.delete()
        self.user.delete()

    def test_order_creation(self):
        self.assertEqual(self.order.customer.user.username, self.username)
        self.assertEqual(self.order.total_price, Decimal('1000.00'))
        self.assertEqual(self.order.status, 'new')

    def test_order_str_method(self):
        expected = f"Заказ №{self.order.id} от {self.customer}"
        self.assertEqual(str(self.order), expected)

    def test_order_status_display(self):
        self.assertEqual(self.order.get_status_display(), 'Новый')

        self.order.status = 'delivered'
        self.order.save()
        self.assertEqual(self.order.get_status_display(), 'Доставлен')
