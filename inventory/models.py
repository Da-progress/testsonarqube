from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название поставщика")
    contact_person = models.CharField(max_length=200, blank=True, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Адрес")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул (SKU)")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.FloatField(default=0.0, verbose_name="Цена (₽)")
    quantity = models.IntegerField(default=0, verbose_name="Количество на складе")
    min_quantity = models.IntegerField(default=0, verbose_name="Минимальный остаток")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products", verbose_name="Категория"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products", verbose_name="Поставщик"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.sku}]"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    @property
    def total_value(self):
        return round(self.price * self.quantity, 2)


MOVEMENT_TYPES = [
    ("in", "Приход"),
    ("out", "Расход"),
    ("adj", "Корректировка"),
]


class StockMovement(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="movements", verbose_name="Товар"
    )
    movement_type = models.CharField(
        max_length=10, choices=MOVEMENT_TYPES, verbose_name="Тип движения"
    )
    quantity = models.IntegerField(verbose_name="Количество")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата/время")

    class Meta:
        verbose_name = "Движение товара"
        verbose_name_plural = "Движения товаров"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} — {self.product.name} ({self.quantity} шт.)"

    def save(self, *args, **kwargs):
        """Auto-update product quantity on save."""
        if self.pk is None:  # new record only
            if self.movement_type == "in":
                self.product.quantity += self.quantity
            elif self.movement_type == "out":
                self.product.quantity -= self.quantity
            elif self.movement_type == "adj":
                self.product.quantity = self.quantity
            self.product.save()
        super().save(*args, **kwargs)
