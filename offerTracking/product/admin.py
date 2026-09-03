from django.contrib import admin

from .models import Brand, Product, Stock


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'brand', 'cost', 'list_price')
	search_fields = ('name', 'brand__name', 'technical_description')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
	list_display = ('product', 'quantity', 'last_updated_at')
	list_filter = ('last_updated_at',)
	search_fields = ('product__name', 'product__brand__name')
	readonly_fields = ('last_updated_at',)
