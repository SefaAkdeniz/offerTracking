from django.contrib import admin
from .models import Customer, CustomerContact
from django.contrib.admin import RelatedOnlyFieldListFilter



class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'city', 'offer_temporarily_closed', 'discount_rate', 'responsible_personnel', 'first_relationship_date')
    #list_display_links = ('company_name', 'email', 'phone', 'city', 'discount_rate', 'responsible_personnel', 'first_relationship_date')
    list_filter = (('responsible_personnel',RelatedOnlyFieldListFilter),'offer_temporarily_closed' )
    #list_select_related = ('responsible_personnel',)
    search_fields = (
        'company_name',
        'email',
        'phone',
        'contacts__email',
        'contacts__phone',
    )
    readonly_fields = ('first_relationship_date',)
    list_per_page = 15
    #list_max_show_all = 5
    #save_on_top = True
    autocomplete_fields = ('responsible_personnel',)
    #preserve_filters = True
    search_help_text = 'Firma adı, e-posta veya telefon numarası ile arayın.'
    ordering = ('company_name',)
    date_hierarchy = 'first_relationship_date'
    
    inlines = (CustomerContactInline,)
    fieldsets = (
    ('FİRMA BİLGİLERİ', {
        'fields': (
            'company_name',
            'phone',
            'email',
            'address',
            'city',
            'offer_temporarily_closed',
        )
    }),
    ('TİCARİ BİLGİLERİ', {
        'fields': (
            'discount_rate',
            'responsible_personnel',
        )
    }),
    ('İLİŞKİ BİLGİLERİ', {
        'fields': (
            'first_relationship_date',
        )
    }),   
    )

@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')