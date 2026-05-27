"""
Management command: populate the database with demo data.
Usage: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from inventory.models import Category, Supplier, Product, StockMovement


CATEGORIES = [
    ("Электроника", "Компьютеры, телефоны, гаджеты"),
    ("Офисные принадлежности", "Бумага, ручки, папки"),
    ("Мебель", "Столы, стулья, шкафы"),
    ("Инструменты", "Ручной и электрический инструмент"),
    ("Расходные материалы", "Картриджи, провода, аксессуары"),
]

SUPPLIERS = [
    ("ООО «ТехноТрейд»", "Иванов А.В.", "+7 495 111-22-33", "info@technotrade.ru"),
    ("ИП Смирнов Д.К.", "Смирнов Д.К.", "+7 812 444-55-66", "smirnov@mail.ru"),
    ("АО «Глобал Сапплай»", "Петрова М.И.", "+7 499 777-88-99", "supply@global.ru"),
    ("ООО «Офис Плюс»", "Козлов Р.Б.", "+7 495 000-11-22", "kozlov@officeplus.ru"),
]

PRODUCTS = [
    ("Ноутбук Lenovo IdeaPad 3", "NB-001", 49990, 5, 2, 0),
    ("Монитор Samsung 24\"", "MON-024", 18500, 12, 3, 0),
    ("Клавиатура Logitech K120", "KB-120", 890, 30, 10, 0),
    ("Мышь Logitech M100", "MS-100", 590, 25, 10, 0),
    ("Бумага A4 500л", "PAP-A4", 350, 200, 50, 1),
    ("Ручка шариковая синяя (уп. 50)", "PEN-BLU", 250, 40, 20, 1),
    ("Папка-скоросшиватель А4", "FOL-A4", 45, 150, 50, 1),
    ("Картридж HP 85A", "CART-85A", 1200, 8, 5, 4),
    ("Кресло офисное Helmi", "CHR-HLM", 8900, 7, 2, 2),
    ("Стол письменный 120x60", "TBL-120", 5500, 4, 1, 2),
    ("Дрель-шуруповёрт Bosch GSR 12V", "DRL-GSR", 6800, 6, 2, 3),
    ("USB-кабель 1м Type-C", "CBL-TC1", 299, 100, 30, 4),
    ("Сетевой фильтр 5 розеток", "FLT-5R", 799, 20, 5, 4),
    ("Блокнот А5 80л", "NTB-A5", 120, 80, 20, 1),
    ("Маркер перманентный Stabilo", "MRK-STB", 89, 60, 20, 1),
]


class Command(BaseCommand):
    help = "Заполняет базу данных демонстрационными данными"

    def handle(self, *args, **kwargs):
        self.stdout.write("Создаём категории…")
        cats = []
        for name, desc in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
            cats.append(cat)

        self.stdout.write("Создаём поставщиков…")
        sups = []
        for name, contact, phone, email in SUPPLIERS:
            sup, _ = Supplier.objects.get_or_create(
                name=name,
                defaults={"contact_person": contact, "phone": phone, "email": email}
            )
            sups.append(sup)

        self.stdout.write("Создаём товары…")
        for name, sku, price, qty, min_qty, cat_idx in PRODUCTS:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "price": price,
                    "quantity": qty,
                    "min_quantity": min_qty,
                    "category": cats[cat_idx],
                    "supplier": random.choice(sups),
                }
            )
            if created:
                StockMovement.objects.create(
                    product=product,
                    movement_type="in",
                    quantity=qty,
                    comment="Начальный остаток (seed)"
                )

        self.stdout.write(self.style.SUCCESS("✅ Демо-данные успешно загружены!"))
