"""
Root URL Configuration for EIAMS
=================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns
import django.conf.urls.i18n

urlpatterns = [
    # Language switcher endpoint (must be outside i18n_patterns)
    path('i18n/', include('django.conf.urls.i18n')),
]

# Media files must be served regardless of DEBUG so uploaded profile pictures
# and other user-uploaded files are accessible in both dev and local production.
# Static files are handled by WhiteNoise middleware in production.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/', permanent=False)),
    path('accounts/',      include('apps.accounts.urls')),
    path('inventory/',     include('apps.inventory.urls')),
    path('assets/',        include('apps.assets.urls')),
    path('stock/',         include('apps.stock.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reports/',       include('apps.reports.urls')),
    path('dashboard/',     include('apps.dashboard.urls')),
    prefix_default_language=False,
)

handler404 = 'apps.accounts.views.error_404'
handler500 = 'apps.accounts.views.error_500'
handler403 = 'apps.accounts.views.error_403'

admin.site.site_header = "EIAMS Administration"
admin.site.site_title  = "EIAMS Admin"
admin.site.index_title = "Enterprise Inventory & Asset Management"
