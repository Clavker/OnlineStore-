from django import forms
from .models import CartItem


class CartAddForm(forms.Form):
    """Форма для добавления товара в корзину"""
    product_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Количество',
        widget=forms.NumberInput(attrs={'class': 'quantity-input', 'min': '1'})
    )

    def clean_quantity(self):
        """Валидация количества"""
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
        """Валидация количества"""
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise forms.ValidationError('Количество не может быть отрицательным')
        return quantity


class OrderForm(forms.Form):
    """Форма для оформления заказа"""
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
        queryset=CartItem.objects.none(),  # Пустой queryset, будет заменён
        label='Корзина',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        """Инициализация формы с актуальными корзинами"""
        super().__init__(*args, **kwargs)
        # Здесь можно установить актуальный queryset для cart
        # self.fields['cart'].queryset = Cart.objects.filter(...)