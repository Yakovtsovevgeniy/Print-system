from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('', include('api.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('swagger-ui/',
         TemplateView.as_view(template_name='swagger-ui.html', extra_context={'schema_url': 'openapi-schema'}),
         name='swagger-ui'),
    path('openapi', get_schema_view(title="Print_system", description="API for print system", version="1.0.0"),
         name='openapi-schema'),
]
