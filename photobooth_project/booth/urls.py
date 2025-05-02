from django.urls import path
from . import views

urlpatterns = [
    path('', views.photobooth_view, name='photobooth'), 
]