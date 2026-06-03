from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Semua URL dari boothapp (dashboard, booth, karyawan, stok, dll)
    path('', include('boothapp.urls')),

    # Autentikasi (Login & Logout)
    path('login/', auth_views.LoginView.as_view(template_name='boothapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Media files (hanya aktif saat DEBUG=True / development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)