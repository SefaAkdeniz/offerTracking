from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'city', 'discount_rate', 'responsible_personnel', 'first_relationship_date')
    #list_display_links = ('company_name', 'email', 'phone', 'city', 'discount_rate', 'responsible_personnel', 'first_relationship_date')
    list_filter = ('responsible_personnel', 'discount_rate')
    search_fields = ('company_name', 'email', 'phone')
    readonly_fields = ('first_relationship_date',)
    list_per_page = 15
    #list_max_show_all = 5
    #save_on_top = True
    autocomplete_fields = (
    'responsible_personnel',
    )
    #preserve_filters = True
    search_help_text = 'Firma adı, e-posta veya telefon numarası ile arayın.'
    ordering = ('company_name',)
    date_hierarchy = 'first_relationship_date'
    list_select_related = ('responsible_personnel',)
    fieldsets = (
    ('Firma Bilgileri', {
        'fields': (
            'company_name',
            'phone',
            'email',
            'address',
            'city',
        )
    }),
    ('Ticari Bilgiler', {
        'fields': (
            'discount_rate',
            'responsible_personnel',
        )
    }),
    ('İlişki Bilgileri', {
        'fields': (
            'first_relationship_date',
        )
    }),   
    )