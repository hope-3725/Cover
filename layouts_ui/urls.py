from django.urls import path

from . import views

app_name = "layouts_ui"

urlpatterns = [
    path("layouts/new/", views.layout_new, name="layout_new"),
    path("layouts/", views.layout_list, name="layout_list"),
    path("layouts/<int:layout_id>/", views.layout_detail, name="layout_detail"),
    path("layouts/<int:layout_id>/edit/", views.layout_edit, name="layout_edit"),
    path("layouts/<int:layout_id>/print/", views.layout_print, name="layout_print"),
]
