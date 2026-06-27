from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('applications.portal_urls')),
    path('', include('applications.urls')),
]

# media support
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
