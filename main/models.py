from django.db import models
from users.models import User


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

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
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

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
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    country = models.CharField(max_length=100, verbose_name="Страна",
                               blank=True)
    city = models.CharField(max_length=100, verbose_name="Город", blank=True)
    street_address = models.CharField(max_length=255,
                                      verbose_name="Улица, дом, квартира",
                                      blank=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}".strip() or self.user.username

    @property
    def cart(self):
        """
        Возвращает активную корзину клиента.
        Если корзины нет - создаёт новую.
        """
        cart = self.carts.first()
        if not cart:
            cart = Cart.objects.create(customer=self)
        return cart

    @property
    def full_address(self):
        """Полный адрес клиента одной строкой"""
        parts = [self.country, self.city, self.street_address]
        return ", ".join(filter(None, parts))


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
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        ordering = ['-created_at']

    def __str__(self):
        return f"Корзина {self.customer} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def total_price(self):
        """Общая стоимость всех товаров в корзине"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Количество позиций в корзине (разных товаров)"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Общее количество единиц товара в корзине"""
        return sum(item.quantity for item in self.items.all())


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
        related_name='cart_items',
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True,
                                    verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ('cart',
                           'product')  # чтобы один товар не дублировался в корзине
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Стоимость данной позиции"""
        return self.product.price * self.quantity


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
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")
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

    # Поля для дополнительной информации из формы заказа
    delivery_name = models.CharField(max_length=255,
                                     verbose_name="Имя получателя", blank=True)
    delivery_address = models.TextField(verbose_name="Адрес доставки",
                                        blank=True)
    contact_email = models.EmailField(verbose_name="Контактный email",
                                      blank=True)
    comment = models.TextField(verbose_name="Комментарий к заказу", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} от {self.customer}"

    @property
    def status_display(self):
        """Отображение статуса на русском"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def total_quantity(self):
        """Общее количество единиц товара в заказе"""
        return sum(item.quantity for item in self.items.all())


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
        related_name='order_items',
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
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Стоимость позиции в заказе"""
        return self.price * self.quantity


class StockMovement(models.Model):
    """Модель для учёта движения товаров (приход/расход)"""
    MOVEMENT_TYPES = [
        ('in', 'Приход'),
        ('out', 'Расход'),
        ('sale', 'Продажа'),
        ('return', 'Возврат'),
        ('adjustment', 'Корректировка'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name="Товар"
    )
    quantity = models.IntegerField(verbose_name="Количество")
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name="Тип движения"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ссылка на документ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кто создал"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Движение товара"
        verbose_name_plural = "Движения товаров"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        """При сохранении движения обновляем остаток товара"""
        # Сохраняем оригинальное количество до изменения
        old_quantity = self.product.stock

        # Сначала сохраняем само движение
        super().save(*args, **kwargs)

        # Затем обновляем остаток товара
        if self.movement_type in ['in', 'return']:
            self.product.stock += self.quantity
        elif self.movement_type in ['out', 'sale']:
            self.product.stock -= self.quantity
        elif self.movement_type == 'adjustment':
            # Для корректировки устанавливаем точное значение
            self.product.stock = self.quantity

        self.product.save()