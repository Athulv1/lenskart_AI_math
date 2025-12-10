from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from app.api import api as app1_api
from app.demo_views import demo_page, demo_projects_api, demo_process_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/app1/', app1_api.urls),
    path('demo/', demo_page, name='demo_page'),
    path('demo/api/projects/', demo_projects_api, name='demo_projects_api'),
    path('demo/api/process/', demo_process_api, name='demo_process_api'),
    
    # Serve media files (works in both DEBUG=True and DEBUG=False)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    
    # Serve static files (works in both DEBUG=True and DEBUG=False)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
]
