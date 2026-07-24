from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('wardrobe/', views.wardrobe_index, name='wardrobe'),
]
