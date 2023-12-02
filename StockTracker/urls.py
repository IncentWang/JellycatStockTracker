from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("startwatch/", views.startwatch, name="startwatch"),
    path("success/", views.success, name="success")
]