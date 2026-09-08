from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from offer.views import offer_pdf

admin.site.site_header = "Yönetim Paneli"
admin.site.site_title = "Yönetim Paneli"
admin.site.index_title = "Site Yönetimi"

urlpatterns = [
    path('offers/<int:offer_id>/pdf/', offer_pdf, name='offer_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

urlpatterns += [
    path('', admin.site.urls),
]