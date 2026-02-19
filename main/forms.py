from django import forms
from .models import Product, CartItem, Order, Cart


class CartAddForm(forms.Form):
    """Форма для добавления товара в корзину"""
    product_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Количество',
        widget=forms.NumberInput(attrs={'class': 'quantity-input', 'min': '1'})
    )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError('Количество должно быть не меньше 1')
        return quantity


class CartItemUpdateForm(forms.Form):
    """Форма для обновления количества товара в корзине"""
    quantity = forms.IntegerField(
        min_value=0,
        label='Количество',
        widget=forms.NumberInput(attrs={'class': 'quantity-input', 'min': '0'})
    )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise forms.ValidationError(
                'Количество не может быть отрицательным')
        return quantity


class OrderForm(forms.Form):
    """Форма для оформления заказа (как в примере из задания)"""
    name = forms.CharField(
        max_length=255,
        label='ФИО',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        max_length=255,
        label='Адрес доставки',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    cart = forms.ModelChoiceField(
        queryset=Cart.objects.all(),
        label='Корзина',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )


# Оставляем старую форму для обратной совместимости, если она где-то используется
class OrderCreateForm(forms.Form):
    """Форма для оформления заказа (наша старая версия)"""
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    cart_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)