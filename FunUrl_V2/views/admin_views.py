from django.shortcuts import render, redirect
from django.http import HttpResponse
from APP.models import *

from django.db.models import Sum


def dashboard(request):
    if request.user.is_authenticated and request.user.is_staff:
        total_user = len(User.objects.all()) - 1
        total_url = (
            len(Public_URL.objects.all())
            + len(Private_URL.objects.all())
            + len(Custom_URL.objects.all())
        )
        total_clicks = (
            (Public_URL.objects.aggregate(Sum("clicks"))["clicks__sum"] or 0)
            + (Private_URL.objects.aggregate(Sum("clicks"))["clicks__sum"] or 0)
            + (Custom_URL.objects.aggregate(Sum("clicks"))["clicks__sum"] or 0)
        )
        context = {
            "total_user": total_user,
            "total_url": total_url,
            "total_clicks": total_clicks,
        }
        return render(request, "./Admin/Admin_dashboard.html", context)

    else:
        return redirect("/login")


def users(request):
    if request.user.is_authenticated and request.user.is_staff:
        user_list = User.objects.all()[1:]
        context = {"user_list": user_list}
        return render(request, "./Admin/Admin_User.html", context)
    else:
        return redirect("/login")


def Users_delete(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        obj = User.objects.get(id=id)
        print(obj)
        obj.delete()
        return redirect("/users")
    else:
        return redirect("/login")


def Guest_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        url_list = guest_url.objects.all()
        context = {"url_list": url_list}
        return render(request, "./Admin/Admin_Guest.html", context)
    else:
        return redirect("/login")


def Public_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        url_list = Public_URL.objects.all()
        context = {"url_list": url_list}
        return render(request, "./Admin/Admin_Public.html", context)
    else:
        return redirect("/login")


def Private_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        url_list = Private_URL.objects.all()
        context = {"url_list": url_list}
        return render(request, "./Admin/Admin_Private.html", context)
    else:
        return redirect("/login")


def Custom_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        url_list = Custom_URL.objects.all()
        context = {"url_list": url_list}
        return render(request, "./Admin/Admin_Custom.html", context)
    else:
        return redirect("/login")
