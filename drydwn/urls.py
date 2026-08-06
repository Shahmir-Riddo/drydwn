from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('diary/', include('diary.urls')),
    path('user/', include('accounts.urls')),
]
