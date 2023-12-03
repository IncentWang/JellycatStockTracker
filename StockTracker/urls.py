from django.urls import path

from . import views

urlpatterns = [
    path("", views.startwatch, name="startwatch"),
    path("success/", views.success, name="success")
]