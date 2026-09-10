from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from .models import Offer, OfferItem
from .views import offer_pdf_response

class OfferItemInline(admin.TabularInline):
	model = OfferItem
	autocomplete_fields = ('product',)
	fields = ('product', 'quantity', 'discount_rate')
	extra = 0

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ('offer_number_display', 'customer', 'customer_contact', 'offer_date', 'discount', 'created_by')
	list_filter = (
        ('customer', RelatedOnlyFieldListFilter),
        ('customer_contact', RelatedOnlyFieldListFilter),
        ('created_by', RelatedOnlyFieldListFilter),
    )
	autocomplete_fields = ('customer','customer_contact',)
	search_fields = ('customer__company_name', 'customer_contact__first_name', 'customer_contact__last_name', 'created_by__username')
	readonly_fields = ('offer_number_display', 'revision_number', 'created_by')
	date_hierarchy = 'offer_date'
	search_help_text = 'Müşteri firma adı, müşteri kişi adı veya kullanıcı adı ile arayın.'
	list_per_page = 15
	inlines = (OfferItemInline,)
	actions = ('download_pdf_with_photos', 'download_pdf_without_photos')
	

	def save_model(self, request, obj, form, change):
		if not change and obj.created_by is None:
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

	@admin.display(description='Teklif numarası')
	def offer_number_display(self, obj):
		return obj.offer_number

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