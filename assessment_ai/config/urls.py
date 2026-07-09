from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── API Docs ──────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # ── API v1 ────────────────────────────────────────
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/roles/', include('apps.roles.urls')),
    path('api/v1/universities/', include('apps.universities.urls')),
    path('api/v1/academic/', include('apps.academic.urls')),
    path('api/v1/courses/', include('apps.courses.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/assessments/', include('apps.assessments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
