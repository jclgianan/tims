"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from inventory import views

urlpatterns = [
    path("", RedirectView.as_view(url="login/", permanent=True)),
    path("admin/", admin.site.urls),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/filter/", views.dashboard, name="stat-cards-filter"),
    path("inventory/", views.inventory_list, name="inventory_list"),
    path("inventory-create/", views.inventory_create, name="inventory_create"),
    path(
        "generate-inventory-id/",
        views.generate_inventory_id,
        name="generate_inventory_id",
    ),
    path("inventory-type/", views.create_inventory_type, name="inventory_type"),
    path(
        "inventory-type/<int:type_id>/",
        views.create_inventory_type,
        name="inventory_type_edit",
    ),
    path("get-type-specs/", views.get_type_specs, name="get_type_specs"),
    path(
        "inventory/<int:inventory_id>/", views.inventory_detail, name="inventory_detail"
    ),
    path("tickets/", include("tickets.urls")),
]
