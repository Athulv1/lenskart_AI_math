from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import redirect
from app.api import api as app1_api
from app.demo_views import demo_page, demo_projects_api, demo_process_api, save_dxf_to_project
from dashboard.api import dashboard_api

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/app1/', app1_api.urls),
    
    path('api/dashboard/', dashboard_api.urls),

    path('', lambda r: redirect('/static/dashboard/index.html')),
    path('canvas', lambda r: redirect('/static/dashboard/canvas.html')),
    path('canvas-preview', lambda r: redirect('/static/dashboard/canvas_preview.html')),
    path('dashboard/', lambda r: redirect('/static/dashboard/index.html')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)