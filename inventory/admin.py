from django.contrib import admin
from .models import Category, Supplier, Product, StockMovement

admin.site.site_header = "Склад — Администрирование"
admin.site.site_title = "Система учёта товаров"
admin.site.index_title = "Панель управления"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "product_count", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Кол-во товаров"


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_person", "phone", "email", "is_active", "product_count"]
    list_filter = ["is_active"]
    search_fields = ["name", "contact_person", "email"]
    ordering = ["name"]
    list_editable = ["is_active"]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Кол-во товаров"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "supplier", "price", "quantity",
                    "min_quantity", "stock_status", "total_value", "updated_at"]
    list_filter = ["category", "supplier"]
    search_fields = ["name", "sku", "description"]
    ordering = ["name"]
    list_editable = ["price", "quantity"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Основное", {"fields": ("name", "sku", "description")}),
        ("Цены и остатки", {"fields": ("price", "quantity", "min_quantity")}),
        ("Классификация", {"fields": ("category", "supplier")}),
        ("Системные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def stock_status(self, obj):
        if obj.is_low_stock:
            return "⚠️ Мало"
        return "✅ Норма"
    stock_status.short_description = "Статус"

    def total_value(self, obj):
        return f"{obj.total_value:,.2f} ₽"
    total_value.short_description = "Стоимость"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "comment", "created_at"]
    list_filter = ["movement_type", "created_at"]
    search_fields = ["product__name", "product__sku", "comment"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
