"""FunUrl_V2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# ! import all views from views folder
from .views import views, admin_views

urlpatterns = [
    # todo Admin urls
    path("admin/", admin.site.urls),
    # path("main_admin/", admin.site.urls),
    path("dashboard/", admin_views.dashboard, name="dashboard"),
    path("users/", admin_views.users, name="users"),
    path("Users_delete/<int:id>", admin_views.Users_delete, name="Users_delete"),
    path("Guest_list/", admin_views.Guest_list, name="Guest_list"),
    path("Public_list/", admin_views.Public_list, name="Public_list"),
    path("Private_list/", admin_views.Private_list, name="Private_list"),
    path("Custom_list/", admin_views.Custom_list, name="Custom_list"),
    # todo Auth
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("delete_account/", views.delete_account, name="delete_account"),
    # todo User urls
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("Public_URL_create/", views.Public_URL_create, name="Public_URL_create"),
    path("Private_URL_create/", views.Private_URL_create, name="Private_URL_create"),
    path("Custom_URL_create/", views.Custom_URL_create, name="Custom_URL_create"),
    path("a/<slug:url>", views.public_redirect_url, name="public_redirect_url"),
    path("p/<slug:url>", views.private_redirect_url, name="private_redirect_url"),
    path(
        "<int:id>/<slug:url>", views.custome_redirect_url, name="custome_redirect_url"
    ),
    path("r/<slug:url>", views.redirect_url, name="redirect"),
    path(
        "redirect_private/<slug:url>", views.redirect_private, name="redirect_private"
    ),
    path("page404/", views.page404, name="page404"),
    path("Pageinactive/", views.Pageinactive, name="Pageinactive"),
    path("profile/", views.profile_page, name="profile"),
    path("Reset_Password/", views.Reset_Password, name="Reset_Password"),
    path("main/", views.main, name="main"),
    path("main/<int:id>", views.dashboard_main, name="dashboard_main"),
    path(
        "Public_Link_delete/<slug:url>",
        views.Public_Link_delete,
        name="Public_Link_delete",
    ),
    path(
        "Public_Link_delete_all/<slug:url>",
        views.Public_Link_delete_all,
        name="Public_Link_delete_all",
    ),
    path(
        "Private_Link_delete/<slug:url>",
        views.Private_Link_delete,
        name="Private_Link_delete",
    ),
    path(
        "Private_Link_delete_all/<slug:url>",
        views.Private_Link_delete_all,
        name="Private_Link_delete_all",
    ),
    path(
        "Custom_Link_delete/<slug:url>",
        views.Custom_Link_delete,
        name="Custom_Link_delete",
    ),
    path(
        "Custom_Link_delete_all/<slug:url>",
        views.Custom_Link_delete_all,
        name="Custom_Link_delete_all",
    ),
    path(
        "Public_Link_details/<slug:url>",
        views.Public_Link_details,
        name="Public_Link_details",
    ),
    path(
        "Private_Link_details/<slug:url>",
        views.Private_Link_details,
        name="Private_Link_details",
    ),
    path(
        "Custom_Link_details/<slug:url>",
        views.Custom_Link_details,
        name="Custom_Link_details",
    ),
    path(
        "Public_Link_details_all/",
        views.Public_Link_details_all,
        name="Public_Link_details_all",
    ),
    path(
        "Private_Link_details_all/",
        views.Private_Link_details_all,
        name="Private_Link_details_all",
    ),
    path(
        "Custom_Link_details_all/",
        views.Custom_Link_details_all,
        name="Custom_Link_details_all",
    ),
    # path("Link_details/<slug:url>", views.Link_details, name="Link_details"),
    path(
        "Public_Link_status_toggle/<slug:url>",
        views.Public_Link_status_toggle,
        name="Public_Link_status_toggle",
    ),
    path(
        "Public_status_toggle/<slug:url>",
        views.Public_status_toggle,
        name="Public_status_toggle",
    ),
    path(
        "private_Link_status_toggle/<slug:url>",
        views.private_Link_status_toggle,
        name="private_Link_status_toggle",
    ),
    path(
        "private_status_toggle/<slug:url>",
        views.private_status_toggle,
        name="private_status_toggle",
    ),
    path(
        "Custom_Link_status_toggle/<slug:url>",
        views.Custom_Link_status_toggle,
        name="Custom_Link_status_toggle",
    ),
    path(
        "Custom_status_toggle/<slug:url>",
        views.Custom_status_toggle,
        name="Custom_status_toggle",
    ),
    path("PrivatePage/", views.PrivatePage, name="PrivatePage"),
    # todo test
    path("main/p/<int:id>", views.public_reports, name="public_reports"),
    path("main/pr/<int:id>", views.private_reports, name="private_reports"),
    path("main/c/<int:id>", views.custom_reports, name="custom_reports"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
