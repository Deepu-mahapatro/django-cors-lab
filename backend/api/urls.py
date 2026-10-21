
from django.urls import path
from .views import home, csrf_token_view

urlpatterns = [
    path("", home, name="home"),
    path("csrf/", csrf_token_view, name="csrf-token"),
]
