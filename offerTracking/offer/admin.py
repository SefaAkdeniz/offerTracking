from collections import defaultdict

from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import format_html
from django.db.models import Prefetch
from .models import Offer, OfferItem, PaymentMethod
from product.models import Stock
from .views import offer_pdf_response


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


class OfferItemInline(admin.TabularInline):
	model = OfferItem
	autocomplete_fields = ('product',)
	fields = ('product', 'quantity', 'discount_rate')
	extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ('offer_number_display', 'customer', 'customer_contact', 'offer_date', 'status', 'stock_available', 'payment_method', 'discount', 'total_display', 'created_by')
	list_filter = (
        ('customer', RelatedOnlyFieldListFilter),
        ('customer_contact', RelatedOnlyFieldListFilter),
		'status',
        ('created_by', RelatedOnlyFieldListFilter),
    )
	autocomplete_fields = ('customer', 'customer_contact', 'payment_method')
	search_fields = ('customer__company_name', 'customer_contact__first_name', 'customer_contact__last_name', 'created_by__username')
	readonly_fields = ('offer_number_display', 'revision_number', 'created_by')
	date_hierarchy = 'offer_date'
	search_help_text = 'Müşteri firma adı, müşteri kişi adı veya kullanıcı adı ile arayın.'
	list_per_page = 15
	inlines = (OfferItemInline,)
	actions = ('download_pdf_with_photos', 'download_pdf_without_photos')

	def get_queryset(self, request):
		return super().get_queryset(request).prefetch_related(
			Prefetch('items', queryset=OfferItem.objects.select_related('product__stock')),
		)
	

	def save_model(self, request, obj, form, change):
		obj._status_before_save = (
			Offer.objects.only('status').get(pk=obj.pk).status if change else None
		)
		if not change and obj.created_by is None:
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

	def save_related(self, request, form, formsets, change):
		super().save_related(request, form, formsets, change)
		if (
			form.instance.status == Offer.Status.SENT
			and form.instance._status_before_save != Offer.Status.SENT
		):
			try:
				self._deduct_offer_stock(form.instance)
			except ValidationError as error:
				previous_status = (
					form.instance._status_before_save or Offer.Status.DRAFT
				)
				Offer.objects.filter(pk=form.instance.pk).update(status=previous_status)
				form.instance.status = previous_status
				self.message_user(
					request,
					'İşlem tamamlanamadı: ' + ' '.join(error.messages),
					level='error',
				)

	def _deduct_offer_stock(self, offer):
		required_by_product = defaultdict(int)
		product_names = {}
		for item in offer.items.select_related('product'):
			required_by_product[item.product_id] += item.quantity
			product_names[item.product_id] = str(item.product)

		with transaction.atomic():
			stocks = {
				stock.product_id: stock
				for stock in Stock.objects.select_for_update().filter(
					product_id__in=required_by_product,
				)
			}
			shortages = []
			for product_id, required_quantity in required_by_product.items():
				stock = stocks.get(product_id)
				available_quantity = stock.quantity if stock else 0
				if available_quantity < required_quantity:
					shortages.append(
						f'{product_names[product_id]}: {required_quantity} adet gerekli, '
						f'{available_quantity} adet stok var.'
					)

			if shortages:
				raise ValidationError(
					'Gönderildi durumuna alınamadı. Stok yetersiz: '
					+ ' '.join(shortages)
				)

			for product_id, required_quantity in required_by_product.items():
				stock = stocks[product_id]
				stock.quantity -= required_quantity
				stock.save()

	@admin.display(description='Teklif numarası')
	def offer_number_display(self, obj):
		return obj.offer_number
	
	@admin.display(description="Toplam")
	def total_display(self,obj):
		return f"{obj.total:.2f}"

	@admin.display(description='Stok durumu')
	def stock_available(self, obj):
		if obj.status != Offer.Status.APPROVED:
			return None

		stock_available = True
		stock_details = []
		for item in obj.items.all():
			stock = getattr(item.product, 'stock', None)
			remaining_quantity = stock.quantity if stock else 0
			required_quantity = max(item.quantity - remaining_quantity, 0)
			if remaining_quantity < item.quantity:
				stock_available = False
			if required_quantity:
				stock_details.append(
					f'{item.product.product_code} - {item.product.name}: '
					f'stok düşüldükten sonra gereken {required_quantity} adet'
				)

		tooltip = '\n'.join(stock_details)
		icon = '✓' if stock_available else '✗'
		color = '#198754' if stock_available else '#dc3545'
		return format_html(
			'<span title="{}" aria-label="{}" style="color: {}; font-size: 1.2em; font-weight: bold; cursor: help;">{}</span>',
			tooltip,
			tooltip,
			color,
			icon,
		)

	def _download_pdf(self, request, queryset, include_photos):
		if queryset.count() != 1:
			self.message_user(request, 'PDF için yalnızca bir teklif seçin.', level='error')
			return
		offer = queryset.select_related('customer', 'created_by').get()
		return offer_pdf_response(offer, include_photos=include_photos)

	@admin.action(description='Fotoğraflı teklif PDF indir')
	def download_pdf_with_photos(self, request, queryset):
		return self._download_pdf(request, queryset, include_photos=True)

	@admin.action(description='Fotoğrafsız teklif PDF indir')
	def download_pdf_without_photos(self, request, queryset):
		return self._download_pdf(request, queryset, include_photos=False)