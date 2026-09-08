from django.contrib import admin

from .models import Offer, OfferItem
from .views import offer_pdf_response


class OfferItemInline(admin.TabularInline):
	model = OfferItem
	autocomplete_fields = (
    'product',
    )
	extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer', 'offer_date', 'revision_number', 'discount_rate', 'created_by')
	list_filter = ('offer_date',)
	search_fields = ('customer__company_name', 'created_by__username')
	readonly_fields = ('revision_number', 'created_by')
	inlines = (OfferItemInline,)
	actions = ('download_pdf_with_photos', 'download_pdf_without_photos')
	

	def save_model(self, request, obj, form, change):
		if not change and obj.created_by is None:
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

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


@admin.register(OfferItem)
class OfferItemAdmin(admin.ModelAdmin):
	list_display = ('offer', 'product', 'quantity')
	list_filter = ('product',)
	search_fields = ('offer__id', 'product__name')
