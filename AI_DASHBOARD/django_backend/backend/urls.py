from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.api import api as app1_api
from app.demo_views import demo_page, demo_projects_api, demo_process_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/app1/', app1_api.urls),
    path('demo/', demo_page, name='demo_page'),
    path('demo/api/projects/', demo_projects_api, name='demo_projects_api'),
    path('demo/api/process/', demo_process_api, name='demo_process_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
