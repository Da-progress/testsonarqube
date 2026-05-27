from django import forms
from .models import Product, Category, Supplier, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "description", "price", "quantity",
                  "min_quantity", "category", "supplier"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "min_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "phone", "email", "address", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "comment"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "movement_type": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class SearchForm(forms.Form):
    SORT_CHOICES = [
        ("name", "Название"),
        ("sku", "Артикул"),
        ("price", "Цена"),
        ("quantity", "Количество"),
        ("created_at", "Дата добавления"),
    ]
    DIR_CHOICES = [("asc", "↑ По возрастанию"), ("desc", "↓ По убыванию")]

    q = forms.CharField(
        required=False, label="Поиск",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Название, SKU, описание…"})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="Все категории",
        label="Категория", widget=forms.Select(attrs={"class": "form-select"})
    )
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES, required=False, label="Сортировка",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    sort_dir = forms.ChoiceField(
        choices=DIR_CHOICES, required=False, label="Направление",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    low_stock = forms.BooleanField(
        required=False, label="Только низкий остаток",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
