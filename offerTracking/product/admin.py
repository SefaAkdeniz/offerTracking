from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Product, ProductGroup, Stock


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('photo_thumbnail', 'product_code', 'name', 'product_group', 'brand', 'cost', 'list_price')
	list_display_links = ('product_code', 'name')
	list_filter = ('product_group', 'brand')
	search_fields = ('product_code', 'name', 'product_group__name', 'brand__name', 'technical_description')
	search_help_text = 'ürün adı, ürün kodu, marka, ürün grubu veya teknik özelliklerle arayın.'
	autocomplete_fields = ('product_group', 'brand')
	list_per_page = 15
	ordering = ('product_code',)
	#list_select_related = True
	#preserve_filters = True
	fieldsets = (
		('ÜRÜN BİLGİLER', {
			'fields': ('product_code', 'name', 'technical_description', 'product_group', 'brand','photo')
		}),
		('FİYATLANDIRMA BİLGİLERİ', {
			'fields': ('cost', 'list_price')
		}),
	)
	@admin.display(description='Fotoğraf')
	def photo_thumbnail(self, obj):
		if not obj.photo:
			return '-'
		return format_html(
			'<img src="{}" width="60" height="60" style="object-fit: contain;" />',
			obj.photo.url,
		)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
	list_display = ('product', 'quantity', 'last_updated_at')
	list_filter = ('last_updated_at',)
	search_fields = ('product__name', 'product__brand__name')
	readonly_fields = ('last_updated_at',)