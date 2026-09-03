from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ('company_name', 'city', 'email', 'phone', 'discount_rate', 'responsible_personnel')
	list_filter = ('city', 'responsible_personnel')
	search_fields = ('company_name', 'email', 'phone')
	readonly_fields = ('first_relationship_date',)

