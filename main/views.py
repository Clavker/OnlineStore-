from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.contrib import messages
from .models import (
    Category, Product, Customer,
    Cart, CartItem, Order, OrderItem
)
from .forms import CartAddForm, CartItemUpdateForm, OrderForm, ProductForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


# ---------- PRODUCT CRUD ----------
def product_list(request):
    """Отображает список всех товаров"""
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})


def product_detail(request, pk):
    """Отображает детальную информацию о товаре"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})


@staff_member_required
def product_create(request):
    """Создание нового товара с использованием ProductForm"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно создан')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'main/product_form.html', {
        'form': form,
        'action': 'Создать'
    })


@staff_member_required
def product_update(request, pk):
    """Редактирование товара с использованием ProductForm"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,
                             f'Товар "{product.name}" успешно обновлён')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'main/product_form.html', {
        'form': form,
        'product': product,
        'action': 'Редактировать'
    })


@staff_member_required
def product_delete(request, pk):
    """Удаление товара (только для персонала)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удалён')
        return redirect('product_list')

    return render(request, 'main/product_confirm_delete.html',
                  {'product': product})


# ---------- CATEGORY CRUD ----------
def category_list(request):
    """Отображает список всех категорий"""
    categories = Category.objects.all()
    return render(request, 'main/category_list.html',
                  {'categories': categories})


def category_detail(request, pk):
    """Отображает товары в конкретной категории"""
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    return render(request, 'main/category_detail.html', {
        'category': category,
        'products': products
    })


@staff_member_required
def category_create(request):
    """Создание новой категории (только для персонала)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Категория создана')
            return redirect('category_list')

    return render(request, 'main/category_form.html', {'action': 'Создать'})


@staff_member_required
def category_update(request, pk):
    """Редактирование категории (только для персонала)"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, 'Категория обновлена')
            return redirect('category_list')

    return render(request, 'main/category_form.html', {
        'category': category,
        'action': 'Редактировать'
    })


@staff_member_required
def category_delete(request, pk):
    """Удаление категории (только для персонала)"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория удалена')
        return redirect('category_list')

    return render(request, 'main/category_confirm_delete.html',
                  {'category': category})


# ---------- CUSTOMER CRUD ----------
@login_required
def customer_list(request):
    """
    Отображает список клиентов.
    Для персонала — всех, для обычных пользователей — только свой профиль
    """
    if request.user.is_staff:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(user=request.user)
    return render(request, 'main/customer_list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    """Отображает детальную информацию о клиенте"""
    customer = get_object_or_404(Customer, pk=pk)
    # Проверка прав
    if not request.user.is_staff and customer.user != request.user:
        messages.error(request, 'У вас нет прав для просмотра этого профиля')
        return redirect('product_list')

    return render(request, 'main/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    """Создание профиля клиента"""
    # Проверяем, нет ли уже профиля у пользователя
    if hasattr(request.user, 'customer'):
        messages.warning(request, 'У вас уже есть профиль покупателя')
        return redirect('customer_detail', pk=request.user.customer.pk)

    if request.method == 'POST':
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        city = request.POST.get('city')
        street_address = request.POST.get('street_address')

        if phone and country and city and street_address:
            customer = Customer.objects.create(
                user=request.user,
                phone=phone,
                country=country,
                city=city,
                street_address=street_address
            )
            messages.success(request, 'Профиль успешно создан')
            return redirect('customer_detail', pk=customer.pk)

    return render(request, 'main/customer_form.html',
                  {'action': 'Создать профиль'})


@login_required
def customer_update(request, pk):
    """Редактирование профиля клиента"""
    customer = get_object_or_404(Customer, pk=pk)

    # Проверка прав
    if not request.user.is_staff and customer.user != request.user:
        messages.error(
            request,
            'У вас нет прав для редактирования этого профиля'
        )
        return redirect('product_list')

    if request.method == 'POST':
        customer.phone = request.POST.get('phone')
        customer.country = request.POST.get('country')
        customer.city = request.POST.get('city')
        customer.street_address = request.POST.get('street_address')
        customer.save()

        messages.success(request, 'Профиль обновлён')
        return redirect('customer_detail', pk=customer.pk)

    return render(request, 'main/customer_form.html', {
        'customer': customer,
        'action': 'Редактировать профиль'
    })


@staff_member_required
def customer_delete(request, pk):
    """Удаление профиля клиента (только для персонала)"""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Профиль клиента удалён')
        return redirect('customer_list')

    return render(request, 'main/customer_confirm_delete.html',
                  {'customer': customer})


# ---------- CART CRUD ----------
@login_required
def cart_list(request):
    """Отображает список корзин текущего пользователя"""
    carts = Cart.objects.filter(customer__user=request.user)
    return render(request, 'main/cart_list.html', {'carts': carts})


@login_required
def cart_detail(request, pk):
    """Отображает детальную информацию о корзине"""
    cart = get_object_or_404(Cart, pk=pk, customer__user=request.user)
    return render(request, 'main/cart_detail.html', {'cart': cart})


@login_required
def cart_create(request):
    """Создаёт новую корзину для текущего пользователя"""
    customer = get_object_or_404(Customer, user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)

    if created:
        messages.success(request, 'Новая корзина создана')
    else:
        messages.info(request, 'Используется существующая корзина')

    return redirect('cart_detail', pk=cart.pk)


@login_required
def cart_add_item(request, pk):
    """Добавление товара в корзину с использованием формы"""
    cart = get_object_or_404(Cart, pk=pk, customer__user=request.user)

    if request.method == 'POST':
        form = CartAddForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            quantity = form.cleaned_data['quantity']

            product = get_object_or_404(Product, pk=product_id)

            # Проверка наличия
            if quantity > product.stock:
                messages.error(
                    request,
                    f'Недостаточно товара на складе. Доступно: {product.stock}'
                )
                return redirect('cart_detail', pk=cart.pk)

            # Добавляем или обновляем позицию в корзине
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                # Если товар уже в корзине, увеличиваем количество
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    messages.error(
                        request,
                        f'Недостаточно товара. В корзине уже '
                        f'{cart_item.quantity}, доступно {product.stock}'
                    )
                    return redirect('cart_detail', pk=cart.pk)

                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(
                    request,
                    f'Количество товара "{product.name}" увеличено '
                    f'до {cart_item.quantity}'
                )
            else:
                messages.success(
                    request,
                    f'Товар "{product.name}" добавлен в корзину'
                )

            return redirect('cart_detail', pk=cart.pk)
        else:
            messages.error(
                request,
                'Ошибка в форме. Проверьте введённые данные.'
            )
    else:
        # GET запрос - получаем product_id из параметров
        product_id = request.GET.get('product_id')
        form = CartAddForm(
            initial={'product_id': product_id} if product_id else None
        )

    # Для GET запроса показываем форму выбора товара
    products = Product.objects.filter(stock__gt=0)
    return render(request, 'main/cart_add_item.html', {
        'form': form,
        'cart': cart,
        'products': products
    })


@login_required
def cart_item_update(request, pk):
    """Обновление количества товара в корзине с использованием формы"""
    cart_item = get_object_or_404(
        CartItem,
        pk=pk,
        cart__customer__user=request.user
    )

    if request.method == 'POST':
        form = CartItemUpdateForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity > cart_item.product.stock:
                messages.error(
                    request,
                    f'Недостаточно товара. Доступно: {cart_item.product.stock}'
                )
            elif quantity <= 0:
                cart_item.delete()
                messages.success(request, 'Товар удалён из корзины')
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Количество обновлено')

            return redirect('cart_detail', pk=cart_item.cart.pk)
    else:
        form = CartItemUpdateForm(initial={'quantity': cart_item.quantity})

    return render(request, 'main/cart_item_form.html', {
        'form': form,
        'cart_item': cart_item
    })


@login_required
def cart_item_delete(request, pk):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(
        CartItem,
        pk=pk,
        cart__customer__user=request.user
    )
    cart_pk = cart_item.cart.pk

    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, 'Товар удалён из корзины')
        return redirect('cart_detail', pk=cart_pk)

    return render(request, 'main/cart_item_confirm_delete.html',
                  {'cart_item': cart_item})


# ---------- ORDER CRUD ----------
@login_required
def order_list(request):
    """Отображает список заказов текущего пользователя"""
    orders = Order.objects.filter(customer__user=request.user)
    return render(request, 'main/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    """Отображает детальную информацию о заказе"""
    order = get_object_or_404(Order, pk=pk, customer__user=request.user)
    return render(request, 'main/order_detail.html', {'order': order})


@login_required
@transaction.atomic
def order_create_from_cart(request, cart_id):
    """Оформление заказа из корзины с использованием формы OrderForm"""
    cart = get_object_or_404(Cart, pk=cart_id, customer__user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            email = form.cleaned_data['email']
            comment = form.cleaned_data.get('comment', '')

            # Проверяем, что корзина не пуста
            if not cart.items.exists():
                messages.error(request, 'Корзина пуста')
                return redirect('cart_detail', pk=cart.pk)

            # Проверяем наличие всех товаров с блокировкой для гонки данных
            for item in cart.items.all():
                product = Product.objects.select_for_update().get(
                    pk=item.product.pk)
                if item.quantity > product.stock:
                    messages.error(
                        request,
                        f'Товара "{product.name}" недостаточно на складе. '
                        f'Доступно: {product.stock}, в корзине: {item.quantity}'
                    )
                    return redirect('cart_detail', pk=cart.pk)

            # Создаём заказ
            total_price = sum(
                item.product.price * item.quantity
                for item in cart.items.all()
            )

            order = Order.objects.create(
                customer=cart.customer,
                total_price=total_price,
                status='new',
                delivery_name=name,
                delivery_address=address,
                contact_email=email,
                comment=comment
            )

            # Переносим позиции из корзины в заказ
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Уменьшаем количество товара на складе
                item.product.stock -= item.quantity
                item.product.save()

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(
                request,
                f'Заказ №{order.id} успешно оформлен!'
            )
            return redirect('order_detail', pk=order.pk)
    else:
        # Передаём в форму текущую корзину и данные пользователя, если есть
        initial_data = {
            'cart': cart.id,
        }
        if hasattr(request.user, 'customer'):
            customer = request.user.customer
            initial_data.update({
                'name': f"{customer.user.last_name} {customer.user.first_name}",
                'address': (
                    f"{customer.country}, {customer.city}, "
                    f"{customer.street_address}"
                ),
                'email': customer.user.email,
            })
        form = OrderForm(initial=initial_data)

    return render(request, 'main/order_create.html', {
        'form': form,
        'cart': cart
    })


@login_required
def order_update_status(request, pk):
    """Обновление статуса заказа (только для персонала)"""
    # Сначала проверяем права
    if not request.user.is_staff:
        messages.error(
            request,
            'У вас нет прав для изменения статуса заказа'
        )
        return redirect('order_detail', pk=pk)

    # Только после проверки прав ищем заказ
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(
                request,
                f'Статус заказа изменён на "{order.get_status_display()}"'
            )

        return redirect('order_detail', pk=order.pk)

    return render(request, 'main/order_status_form.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES
    })


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('product_list')
    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )


def home_view(request):
    """Главная страница"""
    return render(request, 'main/home.html')