from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Product, Category, Supplier, StockMovement
from .forms import ProductForm, CategoryForm, SupplierForm, StockMovementForm, SearchForm
from .db_sa import sa_search_products, sa_warehouse_stats


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    stats = sa_warehouse_stats()
    recent_movements = StockMovement.objects.select_related("product").order_by("-created_at")[:10]
    low_stock_products = Product.objects.filter(quantity__lte=models_min_qty()).order_by("quantity")[:10]
    return render(request, "inventory/dashboard.html", {
        "stats": stats,
        "recent_movements": recent_movements,
        "low_stock_products": low_stock_products,
    })


def models_min_qty():
    from django.db.models import F
    return F("min_quantity")


# ──────────────────────────────────────────────
# Products — CRUD + Search/Sort (via SQLAlchemy)
# ──────────────────────────────────────────────

@login_required
def product_list(request):
    form = SearchForm(request.GET or None)
    query = ""
    sort_by = "name"
    sort_dir = "asc"
    category_id = None
    low_stock = False

    if form.is_valid():
        query = form.cleaned_data.get("q", "")
        sort_by = form.cleaned_data.get("sort_by") or "name"
        sort_dir = form.cleaned_data.get("sort_dir") or "asc"
        cat = form.cleaned_data.get("category")
        category_id = cat.id if cat else None
        low_stock = form.cleaned_data.get("low_stock", False)

    # SA-powered search & sort
    sa_products = sa_search_products(
        query=query, sort_by=sort_by, sort_dir=sort_dir,
        category_id=category_id, low_stock=low_stock
    )

    # Map SA objects → light dicts for template
    products = [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "price": p.price,
            "quantity": p.quantity,
            "min_quantity": p.min_quantity,
            "is_low_stock": p.quantity <= p.min_quantity,
            "category": p.category.name if p.category else "—",
            "supplier": p.supplier.name if p.supplier else "—",
        }
        for p in sa_products
    ]

    return render(request, "inventory/product_list.html", {
        "products": products,
        "form": form,
        "count": len(products),
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.movements.all().order_by("-created_at")[:20]
    return render(request, "inventory/product_detail.html", {
        "product": product,
        "movements": movements,
    })


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        messages.success(request, f"Товар «{product.name}» успешно добавлен.")
        return redirect("product_detail", pk=product.pk)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Добавить товар"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, f"Товар «{product.name}» обновлён.")
        return redirect("product_detail", pk=product.pk)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Редактировать товар", "product": product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Товар «{name}» удалён.")
        return redirect("product_list")
    return render(request, "inventory/confirm_delete.html", {"object": product, "back_url": "product_list"})


# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.prefetch_related("products").order_by("name")
    return render(request, "inventory/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        cat = form.save()
        messages.success(request, f"Категория «{cat.name}» создана.")
        return redirect("category_list")
    return render(request, "inventory/category_form.html", {"form": form, "title": "Добавить категорию"})


@login_required
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=cat)
    if form.is_valid():
        form.save()
        messages.success(request, "Категория обновлена.")
        return redirect("category_list")
    return render(request, "inventory/category_form.html", {"form": form, "title": "Редактировать категорию"})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        cat.delete()
        messages.success(request, "Категория удалена.")
        return redirect("category_list")
    return render(request, "inventory/confirm_delete.html", {"object": cat, "back_url": "category_list"})


# ──────────────────────────────────────────────
# Suppliers
# ──────────────────────────────────────────────

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.prefetch_related("products").order_by("name")
    return render(request, "inventory/supplier_list.html", {"suppliers": suppliers})


@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        sup = form.save()
        messages.success(request, f"Поставщик «{sup.name}» добавлен.")
        return redirect("supplier_list")
    return render(request, "inventory/supplier_form.html", {"form": form, "title": "Добавить поставщика"})


@login_required
def supplier_update(request, pk):
    sup = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=sup)
    if form.is_valid():
        form.save()
        messages.success(request, "Поставщик обновлён.")
        return redirect("supplier_list")
    return render(request, "inventory/supplier_form.html", {"form": form, "title": "Редактировать поставщика"})


@login_required
def supplier_delete(request, pk):
    sup = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        sup.delete()
        messages.success(request, "Поставщик удалён.")
        return redirect("supplier_list")
    return render(request, "inventory/confirm_delete.html", {"object": sup, "back_url": "supplier_list"})


# ──────────────────────────────────────────────
# Stock Movements
# ──────────────────────────────────────────────

@login_required
def movement_list(request):
    movements = StockMovement.objects.select_related("product").order_by("-created_at")
    return render(request, "inventory/movement_list.html", {"movements": movements})


@login_required
def movement_create(request):
    form = StockMovementForm(request.POST or None)
    if form.is_valid():
        mv = form.save()
        messages.success(request, f"Движение товара «{mv.product.name}» зарегистрировано.")
        return redirect("movement_list")
    return render(request, "inventory/movement_form.html", {"form": form, "title": "Добавить движение товара"})


# ──────────────────────────────────────────────
# API — quick JSON endpoints
# ──────────────────────────────────────────────

@login_required
def api_stats(request):
    return JsonResponse(sa_warehouse_stats())
