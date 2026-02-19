from django.db import models
from users.models import User  # импортируем нашу кастомную модель


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name="Цена")
    stock = models.IntegerField(verbose_name="Количество на складе")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Клиент (связь с пользователем)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name="Пользователь"
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street_address = models.CharField(max_length=255,
                                      verbose_name="Улица, дом, квартира")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class Cart(models.Model):
    """Корзина клиента"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name="Клиент"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.customer} от {self.created_at.strftime('%d.%m.%Y')}"


class CartItem(models.Model):
    """Позиция в корзине"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Корзина"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ('cart',
                           'product')  # чтобы один товар не дублировался в корзине

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Клиент"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата заказа")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Общая сумма"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} от {self.customer}"


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на момент заказа"
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"