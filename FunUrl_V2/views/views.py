from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from APP.models import *


from ..decorators import check

import os
import random
import string
import re
from datetime import datetime, timedelta

# from random import randint

from urllib.request import urlopen
import urllib.error
import ssl

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Sum
from django.templatetags.static import static

# !for Caching
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

import subprocess
import requests

# ? Constant Domain name
domain = "http://127.0.0.1:8000"
# domain = "http://192.168.11.130:8000"
# domain = "http://192.168.0.107:8000"
# domain = "http://192.168.29.144:8000"
# domain = "http://10.0.3.78:8000"


# def status(url):
def status(url):
    # url = 'https://www.example.com'
    try:
        response = urlopen(url)
        if response.getcode() != 404 or response.getcode() == 403:
            return True
        else:
            return False
    except urllib.error.URLError as e:
        return False


@check(guest_url)
def index(request):
    return render(request, "index.html", {"short_url": "URL"})


def login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/dashboard")
        else:
            return redirect("/main")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff and user.is_superuser:
                # print(user)
                auth_login(request, user)
                return redirect("/dashboard")
            else:
                auth_login(request, user)
                return redirect("/main")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("/login")

    return render(request, "General/login.html")


def logout(request):
    auth_logout(request)
    return redirect("/")


def Reset_Password(request):
    if request.user.is_authenticated and not request.user.is_staff:
        if request.method == "POST":
            password = request.POST["password"]
            newpassword = request.POST["newpassword"]
            renewpassword = request.POST["renewpassword"]
            # print(password, newpassword, renewpassword)
            if newpassword == renewpassword:
                # print(request.user)
                obj = User.objects.get(username=request.user)
                # obj.password
                if check_password(password, obj.password):
                    obj.set_password(newpassword)
                    obj.save()
                # else:
                # print(False)
        return redirect("/login")
    else:
        return redirect("/login")


def delete_account(request):
    if request.user.is_authenticated:
        user = User.objects.get(name=request.user.name)
        user.delete()
        logout(request)
        return redirect("/login")
    else:
        return redirect("/login")


def register(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phno = request.POST["phno"]
        username = request.POST["username"]
        password = request.POST["password"]
        profile_picture = request.FILES.get("profile_picture", None)

        username_check = User.objects.filter(username=username).exists()
        email_check = User.objects.filter(email=email).exists()

        if username_check == True:
            messages.error(request, "Username Already Exists")
            return redirect("/register")
        if email_check == True:
            messages.error(request, "Email Already Exists")
            return redirect("/register")

        if len(phno) != 10:
            messages.error(request, "Enter a valid Phone number")
            return redirect("/register")

        user = User()
        user.name = name
        user.username = username
        user.email = email
        user.password = make_password(password)
        user.contact = phno
        if profile_picture != None:
            extension = os.path.splitext(profile_picture.name)[1]
            unique_file = username + extension
            user.image.save(unique_file, profile_picture)
        else:
            user.image = "default_pic.png"
        user.save()
        return redirect("/login")

    return render(request, "General/register.html")


@csrf_protect
def create(request):
    if request.method == "POST":
        generatedurl = "URL"
        a = generate()
        date = generate_date()
        url = request.POST["urldata"]
        print(url)
        if is_valid_url(url):
            try:
                context = ssl.create_default_context()
                response = urllib.request.urlopen(url, context=context)
                print(response.getstatus)
            except urllib.error.URLError as e:
                error = f"{e.reason}"
                # print(error)
                if "SSL" in error:
                    # print("SSl")
                    messages.error(
                        request, "The server couldn't fulfill the request.Page SSL"
                    )
                else:
                    messages.error(
                        request,
                        f"The server couldn't fulfill the request.Page {error}",
                    )
            except:
                # cache_key = f"create_{url}"
                # Prev_url = cache.get(cache_key)

                Prev_url = guest_url.objects.filter(ourl=url)

                if Prev_url.exists():
                    a = Prev_url[0].rurl
                else:
                    obj = guest_url()
                    obj.rurl = a
                    obj.ourl = url
                    obj.created_at = date[0]
                    obj.expiry_at = date[1]
                    obj.save()
                generatedurl = domain + "/r/" + a
                # print(">>>>>>>>>", generatedurl)
        else:
            # print("error")
            messages.error(request, "Enter a valid Url !")
        # print(generatedurl)
    return render(request, "index.html", {"short_url": generatedurl, "long_url": url})
    # else:
    #     return redirect("/")


def generate():
    url = "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(5)
    )
    return url


def generate_date():
    current = datetime.now()
    expiry = current + timedelta(hours=24)
    current = current.strftime("%d/%m/%Y, %H:%M:%S")
    expiry = expiry.strftime("%d/%m/%Y, %H:%M:%S")
    return (current, expiry)


def check():
    format = "%d/%m/%Y, %H:%M:%S"
    urls = guest_url.objects.all()

    for i in urls:
        now = datetime.now()
        update = i.expiry_at
        datetime_object2 = datetime.strptime(update, format)
        if datetime_object2 <= now:
            obj = guest_url.objects.get(rurl=i.rurl)
            obj.delete()


def page404(request):
    return render(request, "General/Page404.html")


def Pageinactive(request):
    return render(request, "General/PageInactive.html")


def profile_page(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return render(request, "General/ProfilePage.html")
    else:
        return redirect("/login")


def return_dict(list, key, id=0):
    d = {}
    now = datetime.now()
    if key == 0:
        for row in list:
            date = row.Created_at.split(",")[0]
            if date not in d:
                d[date] = 1
            else:
                d[date] = d[date] + 1

    elif key == 1:
        for row in list:
            if row.url_log not in d:
                d[row.url_log] = row.clicks
                # print(row.url_log)
            else:
                d[row.url_log] += row.clicks
        # print(",,", d)
    elif key == 2:
        for row in list:
            if row.url_log not in d:
                d[row.url_log] = row.clicks
                # print(row.clicks)
            else:
                d[row.url_log] += row.clicks
    # elif key == 2:
    # print(now.month)
    # for row in list:
    # print(row.url_log)
    # print(">>>>>>>>>", d)
    date = d
    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    da = {}
    m = {}
    mm = {}
    y = {}
    dd = {}
    for d in date:
        # print("///", d)
        date_string = d
        date_format = "%d/%m/%Y"
        date_obj = datetime.strptime(date_string, date_format)
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        if month == now.month and year == now.year:
            if d not in da:
                da[d] = date[d]

        if year <= now.year:
            if str(year) not in y:
                y[str(year)] = date[d]
            else:
                y[str(year)] = y[str(year)] + date[d]

        if month <= now.month and year == now.year:
            if month not in m:
                m[month] = date[d]
            else:
                m[month] = m[month] + date[d]

    da = dict(sorted(da.items()))
    m = dict(sorted(m.items()))
    y = dict(sorted(y.items()))
    # print("Current Month :", da)
    # print("all Month :", m)
    for mon in m:
        mm[months[mon]] = m[mon]
    # print("Year :", y)
    # print("Year :", mm)
    # print(da)
    if id == 1:
        return da
    elif id == 2:
        return mm
    elif id == 3:
        return y
    else:
        return da


def main(request):
    if request.user.is_authenticated and not request.user.is_staff:
        date = generate_date()
        date = date[0].split(",")[0]
        url_list = Public_URL.objects.filter(user=request.user)
        total_url = url_list.count()
        url_list1 = Private_URL.objects.filter(user=request.user)
        url_list2 = Custom_URL.objects.filter(user=request.user)
        total_clicks = Public_URL.objects.filter(user=request.user).aggregate(
            Sum("clicks")
        )["clicks__sum"]
        total_clicks_list = Public_URL_Log.objects.filter(user=request.user)
        today_clicks = Public_URL_Log.objects.filter(user=request.user, url_log=date)
        Total_public_url = return_dict(url_list, 0)
        tv, td = [row for row in Total_public_url], [
            Total_public_url[row] for row in Total_public_url
        ]
        Total_number_click = return_dict(total_clicks_list, 1)
        tv1, td1 = [row for row in Total_number_click], [
            Total_number_click[row] for row in Total_number_click
        ]
        today_url_clicks = return_dict(today_clicks, 2)
        tv2, td2 = [row for row in today_url_clicks], [
            today_url_clicks[row] for row in today_url_clicks
        ]

        today_clicks = today_clicks.aggregate(Sum("clicks"))
        today_clicks = today_clicks["clicks__sum"]
        if today_clicks == None:
            today_clicks = 0
        context = {
            "url_id": 1,
            "total_url": total_url,
            "total_clicks": total_clicks,
            "url_list": url_list,
            "url_list1": url_list1,
            "url_list2": url_list2,
            "title": "Public",
            "today_clicks": today_clicks,
            "label_value": td,
            "label_date": tv,
            "label_value1": td1,
            "label_date1": tv1,
            "label_value2": td2,
            "label_date2": tv2,
        }
        return render(request, "includes/main.html", context)
    else:
        return redirect("/login")


def dashboard_main(request, id):
    if request.user.is_authenticated and not request.user.is_staff:
        date = generate_date()
        date = date[0].split(",")[0]
        # print(date)
        total_url = 0
        total_clicks = 0
        # title = "urls"
        url_list = Public_URL.objects.filter(user=request.user)
        url_list1 = Private_URL.objects.filter(user=request.user)
        url_list2 = Custom_URL.objects.filter(user=request.user)
        if id == 1:
            url_id = 1
            # total_url = Public_URL.objects.filter(user=request.user).count()
            total_clicks = Public_URL.objects.filter(user=request.user).aggregate(
                Sum("clicks")
            )["clicks__sum"]
            total_clicks_list = Public_URL_Log.objects.filter(user=request.user)
            today_clicks = Public_URL_Log.objects.filter(
                user=request.user, url_log=date
            )
            Total_public_url = return_dict(url_list, 0)
            tv, td = [row for row in Total_public_url], [
                Total_public_url[row] for row in Total_public_url
            ]
            Total_number_click = return_dict(total_clicks_list, 1)
            tv1, td1 = [row for row in Total_number_click], [
                Total_number_click[row] for row in Total_number_click
            ]
            today_url_clicks = return_dict(today_clicks, 2)
            tv2, td2 = [row for row in today_url_clicks], [
                today_url_clicks[row] for row in today_url_clicks
            ]
            total_url = len(url_list)
            total_clicks = Public_URL.objects.filter(user=request.user).aggregate(
                Sum("clicks")
            )["clicks__sum"]
            title = "Public"
            today_clicks = today_clicks.aggregate(Sum("clicks"))
            today_clicks = today_clicks["clicks__sum"]
            if today_clicks == None:
                today_clicks = 0
            d = return_dict(url_list, 0)
            tv, td = [row for row in d], [d[row] for row in d]
        elif id == 2:
            url_id = 2
            # total_url = Private_URL.objects.filter(user=request.user).count()
            total_clicks = Private_URL.objects.filter(user=request.user).aggregate(
                Sum("clicks")
            )["clicks__sum"]
            total_clicks_list = Private_URL_Log.objects.filter(user=request.user)
            today_clicks = Private_URL_Log.objects.filter(
                user=request.user, url_log=date
            )
            Total_public_url = return_dict(url_list, 0)
            tv, td = [row for row in Total_public_url], [
                Total_public_url[row] for row in Total_public_url
            ]
            Total_number_click = return_dict(total_clicks_list, 1)
            tv1, td1 = [row for row in Total_number_click], [
                Total_number_click[row] for row in Total_number_click
            ]
            # print("....", url_list)
            today_url_clicks = return_dict(today_clicks, 2)
            tv2, td2 = [row for row in today_url_clicks], [
                today_url_clicks[row] for row in today_url_clicks
            ]
            total_url = len(url_list1)
            today_clicks = today_clicks.aggregate(Sum("clicks"))
            title = "Private"
            today_clicks = Private_URL_Log.objects.filter(
                user=request.user, url_log=date
            ).aggregate(Sum("clicks"))
            today_clicks = today_clicks["clicks__sum"]
            if today_clicks == None:
                today_clicks = 0
            d = return_dict(url_list1, 0)
            tv, td = [row for row in d], [d[row] for row in d]

        elif id == 3:
            url_id = 3
            # total_url = Private_URL.objects.filter(user=request.user).count()
            total_clicks = Custom_URL.objects.filter(user=request.user).aggregate(
                Sum("clicks")
            )["clicks__sum"]
            total_clicks_list = Custom_URL_Log.objects.filter(user=request.user)
            today_clicks = Custom_URL_Log.objects.filter(
                user=request.user, url_log=date
            )
            Total_public_url = return_dict(url_list, 0)
            tv, td = [row for row in Total_public_url], [
                Total_public_url[row] for row in Total_public_url
            ]
            Total_number_click = return_dict(total_clicks_list, 1)
            tv1, td1 = [row for row in Total_number_click], [
                Total_number_click[row] for row in Total_number_click
            ]
            today_url_clicks = return_dict(today_clicks, 2)
            tv2, td2 = [row for row in today_url_clicks], [
                today_url_clicks[row] for row in today_url_clicks
            ]
            total_url = len(url_list2)
            total_clicks = Custom_URL.objects.filter(user=request.user).aggregate(
                Sum("clicks")
            )["clicks__sum"]
            title = "Custom"
            today_clicks = today_clicks.aggregate(Sum("clicks"))
            today_clicks = today_clicks["clicks__sum"]
            if today_clicks == None:
                today_clicks = 0
            d = return_dict(url_list2, 0)
            tv, td = [row for row in d], [d[row] for row in d]
            # print(url_id)
        # context = {
        #     "url_id": url_id,
        #     "total_url": total_url,
        #     "total_clicks": total_clicks,
        #     "url_list": url_list,
        #     "url_list1": url_list1,
        #     "url_list2": url_list2,
        #     "title": title,
        #     "today_clicks": today_clicks,
        #     "label_value": td,
        #     "label_date": tv,
        # }
        context = {
            "title": title,
            "url_id": url_id,
            "total_url": total_url,
            "total_clicks": total_clicks,
            "url_list": url_list,
            "url_list1": url_list1,
            "url_list2": url_list2,
            "today_clicks": today_clicks,
            "label_value": td,
            "label_date": tv,
            "label_value1": td1,
            "label_date1": tv1,
            "label_value2": td2,
            "label_date2": tv2,
        }
        return render(request, "includes/main.html", context)
    else:
        return redirect("/login")


def redirect_url(request, url):
    try:
        obj = guest_url.objects.get(rurl=url)
        return redirect(obj.ourl)
    except Exception:
        return render(request, "General/Page404.html")


def public_redirect_url(request, url):
    date = generate_date()
    date = date[0].split(",")[0]
    try:
        obj = Public_URL.objects.get(short_url=url)
        if obj.status == True:
            obj.clicks += 1
            log_check = Public_URL_Log.objects.filter(url=obj, url_log=date)
            obj.save()
            if log_check.exists():
                obj_click = Public_URL_Log.objects.get(
                    user=request.user, url=obj, url_log=date
                )
                obj_click.clicks += 1
                obj_click.save()
                return redirect(obj.long_url)
            else:
                log = Public_URL_Log()
                log.user = request.user
                log.url = obj
                log.url_log = date
                log.clicks = 1
                log.save()
                return redirect(obj.long_url)
        else:
            return redirect("/Pageinactive")
    except Exception:
        return render(request, "General/Page404.html")


def custome_redirect_url(request, id, url):
    # print(id, url)
    date = generate_date()
    date = date[0].split(",")[0]
    try:
        obj = Custom_URL.objects.get(
            user_id=id,
            short_url=url,
        )
        # print(obj)
        if obj.status == True:
            obj.clicks += 1
            log_check = Custom_URL_Log.objects.filter(url=obj, url_log=date)
            obj.save()
            # print(log_check)
            if log_check.exists():
                obj_click = Custom_URL_Log.objects.get(url=obj, url_log=date)
                # print(obj_click)
                obj_click.clicks += 1
                obj_click.save()
                return redirect(obj.long_url)
            else:
                log = Custom_URL_Log()
                log.user = request.user
                log.url = obj
                log.url_log = date
                log.clicks = 1
                log.save()
                return redirect(obj.long_url)
        else:
            return redirect("/Pageinactive")
    except Exception:
        return render(request, "General/Page404.html")


def redirect_private(request, url):
    date = generate_date()
    date = date[0].split(",")[0]
    if request.method == "POST":
        pwd_data = request.POST["pwd"]
        try:
            obj = Private_URL.objects.get(short_url=url)
            if obj.status == True:
                if obj.url_password == pwd_data:
                    obj.clicks += 1
                    log_check = Private_URL_Log.objects.filter(url=obj, url_log=date)
                    obj.save()
                    if log_check.exists():
                        obj_click = Private_URL_Log.objects.get(
                            user=request.user, url=obj, url_log=date
                        )
                        obj_click.clicks += 1
                        obj_click.save()
                        return redirect(obj.long_url)
                    else:
                        log = Private_URL_Log()
                        log.user = request.user
                        log.url = obj
                        log.url_log = date
                        log.clicks = 1
                        log.save()
                        return redirect(obj.long_url)
                else:
                    messages.error(request, "Incorrect Password.")
                    return redirect(f"/p/{url}")
            else:
                return redirect("/Pageinactive")
        except Exception:
            return render(request, "General/Page404.html")
    # return redirect(f"/p/{url}")


def private_redirect_url(request, url):
    try:
        obj = Private_URL.objects.get(short_url=url)
        if obj.status == True:
            return render(request, "General/PrivatePage.html", {"url": url})
        else:
            return redirect("/Pageinactive")
    except Exception:
        return render(request, "General/Page404.html")


def Public_URL_create(request):
    if request.user.is_authenticated and not request.user.is_staff:
        generatedurl = "URL"
        url = "Paste here.."
        url_list = Public_URL.objects.filter(user=request.user)
        Total_public_url = return_dict(url_list, 0)
        tv, td = [row for row in Total_public_url], [
            Total_public_url[row] for row in Total_public_url
        ]

        if request.method == "POST":
            url = request.POST["urldata"]
            if is_valid_url(url):
                try:
                    context = ssl.create_default_context()
                    response = urllib.request.urlopen(url, context=context)
                except urllib.error.URLError as e:
                    error = f"{e.reason}"
                    if "SSL" in error:
                        messages.error(
                            request, "The server couldn't fulfill the request.Page SSL"
                        )
                    else:
                        messages.error(
                            request,
                            f"The server couldn't fulfill the request.Page {error}",
                        )
                except:
                    messages.error(
                        request,
                        f"The Url does not Exist",
                    )
                else:
                    Prev_url = Public_URL.objects.filter(
                        user=request.user, long_url=url
                    )
                    if Prev_url.exists():
                        a = Prev_url[0].short_url
                        obj = Public_URL.objects.get(short_url=a)
                        if obj.status == False:
                            obj.status = True
                            obj.save()
                    else:
                        a = generate()
                        date = generate_date()[0]
                        url_obj = Public_URL()
                        url_obj.user = request.user
                        url_obj.short_url = a
                        url_obj.long_url = url
                        url_obj.Created_at = date
                        url_obj.status = True
                        url_obj.save()
                    generatedurl = domain + "/a/" + a
            else:
                # print("error")
                messages.error(request, "Enter a valid Url !")
        context = {
            "short_url": generatedurl,
            "long_url": url,
            "url_list": url_list,
            "label_value": td,
            "label_date": tv,
        }
        return render(request, "General/Url/Public_URL.html", context)
    else:
        return redirect("/login")


def Private_URL_create(request):
    if request.user.is_authenticated and not request.user.is_staff:
        generatedurl = "URL"
        password = ""
        url = "Paste here.."
        url_list = Private_URL.objects.filter(user=request.user)
        Total_public_url = return_dict(url_list, 0)
        tv, td = [row for row in Total_public_url], [
            Total_public_url[row] for row in Total_public_url
        ]
        if request.method == "POST":
            url = request.POST["urldata"]
            pwd = request.POST["pwd"]
            if is_valid_url(url):
                try:
                    context = ssl.create_default_context()
                    response = urllib.request.urlopen(url, context=context)
                except urllib.error.URLError as e:
                    error = f"{e.reason}"
                    if "SSL" in error:
                        messages.error(
                            request, "The server couldn't fulfill the request.Page SSL"
                        )
                    else:
                        messages.error(
                            request,
                            f"The server couldn't fulfill the request.Page {error}",
                        )
                except:
                    messages.error(
                        request,
                        f"The Url does not Exist",
                    )
                else:
                    Prev_url = Private_URL.objects.filter(
                        user=request.user, long_url=url
                    )
                    if Prev_url.exists():
                        a = Prev_url[0].short_url
                        obj = Private_URL.objects.get(short_url=a)
                        password = obj.url_password
                        if obj.status == False:
                            obj.status = True
                            obj.save()
                    else:
                        a = generate()
                        date = generate_date()[0]
                        url_obj = Private_URL()
                        url_obj.user = request.user
                        url_obj.short_url = a
                        url_obj.long_url = url
                        url_obj.url_password = pwd
                        url_obj.Created_at = date
                        url_obj.status = True
                        url_obj.save()
                    generatedurl = domain + "/p/" + a
            else:
                # print("error")
                messages.error(request, "Enter a valid Url !")
        context = {
            "short_url": generatedurl,
            "long_url": url,
            "password": password,
            "url_list": url_list,
            "label_value": td,
            "label_date": tv,
        }
        return render(request, "General/Url/Private_URL.html", context)
    else:
        return redirect("/login")
    # return render(request, "General/Url/Custome_URL.html", context)


def Custom_URL_create(request):
    if request.user.is_authenticated and not request.user.is_staff:
        user_id = request.user.id
        generatedurl = "URL"
        name = "Name"
        password = ""
        url = "URL"
        url_list = Custom_URL.objects.filter(user=request.user)
        Total_public_url = return_dict(url_list, 0)
        tv, td = [row for row in Total_public_url], [
            Total_public_url[row] for row in Total_public_url
        ]
        if request.method == "POST":
            url = request.POST["urldata"]
            urlname = request.POST["urlname"]

            if len(urlname) <= 10 and len(urlname) > 0:
                a = urlname
                # print(">>>>>>>>>>>>", urlname)
                if is_valid_url(url):
                    try:
                        context = ssl.create_default_context()
                        response = urllib.request.urlopen(url, context=context)
                    except urllib.error.URLError as e:
                        error = f"{e.reason}"
                        if "SSL" in error:
                            messages.error(
                                request,
                                "The server couldn't fulfill the request.Page SSL",
                            )
                        else:
                            messages.error(
                                request,
                                f"The server couldn't fulfill the request.Page {error}",
                            )
                    except:
                        messages.error(
                            request,
                            f"The Url does not Exist",
                        )
                    else:
                        Prev_url = Custom_URL.objects.filter(
                            user=request.user, long_url=url
                        )
                        if Prev_url.exists():
                            a = Prev_url[0].short_url
                            # print("Prev : ", a)
                            check_short_url = Custom_URL.objects.filter(
                                user=request.user, short_url=urlname
                            )
                            if check_short_url.exists():
                                messages.error(request, "Short name already exist")
                                name = urlname
                            else:
                                obj = Custom_URL.objects.get(short_url=a)
                                if obj.status == False:
                                    obj.status = True
                                    obj.save()
                                obj.short_url = urlname
                                # print(">>>>>>", obj.short_url)
                                obj.save()
                                a = urlname
                        else:
                            check_short_url = Custom_URL.objects.filter(
                                user=request.user, short_url=urlname
                            )
                            if check_short_url.exists():
                                messages.error(request, "Short name already exist")
                                name = urlname
                            else:
                                a = urlname
                                date = generate_date()[0]
                                url_obj = Custom_URL()
                                url_obj.user = request.user
                                url_obj.short_url = a
                                url_obj.long_url = url
                                url_obj.Created_at = date
                                url_obj.status = True
                                url_obj.save()
                                name = a
                        generatedurl = domain + f"/{user_id}/" + a
                else:
                    # print("error")
                    messages.error(request, "Enter a valid Url !")
            else:
                messages.error(request, "Length of name should be 1 to 10")
        # print(Total_public_url)
        context = {
            "user_id": user_id,
            "name": name,
            "short_url": generatedurl,
            "long_url": url,
            "password": password,
            "url_list": url_list,
            "label_value": td,
            "label_date": tv,
        }
        return render(request, "General/Url/Custome_URL.html", context)
    else:
        return redirect("/login")


def PrivatePage(request):
    return render(request, "General/PrivatePage.html")


def Public_Link_delete(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Public_URL.objects.get(short_url=url)
        obj.delete()
        return redirect("/Public_URL_create")
    else:
        return redirect("/login")


def Private_Link_delete(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Private_URL.objects.get(short_url=url)
        obj.delete()
        return redirect("/Private_URL_create")
    else:
        return redirect("/login")


def Custom_Link_delete(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Custom_URL.objects.get(short_url=url, user=request.user)
        obj.delete()
        return redirect("/Custom_URL_create")
    else:
        return redirect("/login")


def Public_Link_delete_all(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Public_URL.objects.get(short_url=url)
        obj.delete()
        return redirect("/Public_Link_details_all")
    else:
        return redirect("/login")


def Private_Link_delete_all(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Private_URL.objects.get(short_url=url)
        obj.delete()
        return redirect("/Private_Link_details_all")
    else:
        return redirect("/login")


def Custom_Link_delete_all(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Custom_URL.objects.get(short_url=url, user=request.user)
        obj.delete()
        return redirect("/Custom_Link_details_all")
    else:
        return redirect("/login")


def Public_Link_status_toggle(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Public_URL.objects.get(short_url=url)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()
        return redirect("/Public_URL_create")
    else:
        return redirect("/login")


def Public_status_toggle(request, url):
    # print("status list: ", url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Public_URL.objects.get(short_url=url)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()

        return redirect(f"/Public_Link_details/{url}")
    else:
        return redirect("/login")


def private_Link_status_toggle(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Private_URL.objects.get(short_url=url)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()

        return redirect("/Private_URL_create")
    else:
        return redirect("/login")


def private_status_toggle(request, url):
    # print("status list: ", url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Private_URL.objects.get(short_url=url)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()

        return redirect(f"/Private_Link_details/{url}")
    else:
        return redirect("/login")


def Custom_Link_status_toggle(request, url):
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Custom_URL.objects.get(short_url=url, user=request.user)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()

        return redirect("/Custom_URL_create")
    else:
        return redirect("/login")


def Custom_status_toggle(request, url):
    # print("status list: ", url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Custom_URL.objects.get(short_url=url, user=request.user)
        if obj.status == True:
            obj.status = False
        else:
            obj.status = True
        obj.save()

        return redirect(f"/Custom_Link_details/{url}")
    else:
        return redirect("/login")


def is_valid_url(url):
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9-]+\.)+[A-Z]{2,}|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(url_pattern.match(url))


def Public_Link_details(request, url):
    # print(url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Public_URL.objects.get(short_url=url)
        url_list = Public_URL.objects.filter(user=request.user)
        context = {
            "url": obj,
            "short_url": f"{domain}/a/{url}",
            "long_url": obj.long_url,
            "created_at": obj.Created_at,
            "url_list": url_list,
        }
        return render(request, "General/Url/Public_URL_details.html", context)
    else:
        return redirect("/login")


def Private_Link_details(request, url):
    # print(url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Private_URL.objects.get(short_url=url)
        url_list = Private_URL.objects.filter(user=request.user)
        context = {
            "url": obj,
            "short_url": f"{domain}/p/{url}",
            "long_url": obj.long_url,
            "created_at": obj.Created_at,
            "url_list": url_list,
            "pwd": obj.url_password,
        }
        return render(request, "General/Url/Private_URL_details.html", context)
    else:
        return redirect("/login")


def Custom_Link_details(request, url):
    # print(url)
    if request.user.is_authenticated and not request.user.is_staff:
        obj = Custom_URL.objects.get(short_url=url, user=request.user)
        url_list = Custom_URL.objects.filter(user=request.user)
        # print(url)
        context = {
            "url": obj,
            "short_url": f"{domain}/{obj.user_id}/{url}",
            "long_url": obj.long_url,
            "created_at": obj.Created_at,
            "url_list": url_list,
        }
        return render(request, "General/Url/Custom_URL_details.html", context)
    else:
        return redirect("/login")


def Public_Link_details_all(request):
    # image = static("assets/img/default_pic.png")
    # print(image)
    if request.user.is_authenticated and not request.user.is_staff:
        url_list = Public_URL.objects.filter(user=request.user)
        if len(url_list) != 0:
            obj = Public_URL.objects.get(short_url=url_list[0].short_url)
            context = {
                "url": url_list[0],
                "short_url": f"{domain}/a/{url_list[0].short_url}",
                "long_url": obj.long_url,
                "created_at": obj.Created_at,
                "url_list": url_list,
            }
        else:
            context = {
                "url": "NA",
                "short_url": "NA",
                "long_url": "NA",
                "created_at": "NA",
                "url_list": url_list,
            }
        # print(context)
        return render(request, "General/Url/Public_URL_details.html", context)
    else:
        return redirect("/login")


def Private_Link_details_all(request):
    if request.user.is_authenticated and not request.user.is_staff:
        url_list = Private_URL.objects.filter(user=request.user)
        if len(url_list) != 0:
            obj = Private_URL.objects.get(short_url=url_list[0].short_url)
            context = {
                "url": url_list[0],
                "short_url": f"{domain}/p/{url_list[0].short_url}",
                "long_url": obj.long_url,
                "created_at": obj.Created_at,
                "url_list": url_list,
                "pwd": obj.url_password,
            }
        else:
            context = {
                "url": "NA",
                "short_url": "NA",
                "long_url": "NA",
                "created_at": "NA",
                "url_list": url_list,
                "pwd": "NA",
            }
        # print(context)
        return render(request, "General/Url/Private_URL_details.html", context)
    else:
        return redirect("/login")


def Custom_Link_details_all(request):
    if request.user.is_authenticated and not request.user.is_staff:
        url_list = Custom_URL.objects.filter(user=request.user)
        if len(url_list) != 0:
            obj = Custom_URL.objects.get(
                short_url=url_list[0].short_url, user=request.user
            )
            context = {
                "url": url_list[0],
                "short_url": f"{domain}/{obj.user_id}/{url_list[0].short_url}",
                "long_url": obj.long_url,
                "created_at": obj.Created_at,
                "url_list": url_list,
            }
        else:
            context = {
                "url": "NA",
                "short_url": "NA",
                "long_url": "NA",
                "created_at": "NA",
                "url_list": url_list,
            }
        # print(context)
        return render(request, "General/Url/Custom_URL_details.html", context)
    else:
        return redirect("/login")


def reports(request, key, id):
    date = generate_date()
    date = date[0].split(",")[0]
    url_list = Public_URL.objects.filter(user=request.user)
    url_list1 = Private_URL.objects.filter(user=request.user)
    url_list2 = Custom_URL.objects.filter(user=request.user)

    if key == 1:
        title = "Public"
        total_url = url_list.count()
        total_clicks = Public_URL.objects.filter(user=request.user).aggregate(
            Sum("clicks")
        )["clicks__sum"]
        total_clicks_list = Public_URL_Log.objects.filter(user=request.user)
        today_clicks = Public_URL_Log.objects.filter(user=request.user, url_log=date)
        Total_public_url = return_dict(url_list, 0, id)
        Total_number_click = return_dict(total_clicks_list, 1, id)
        today_url_clicks = return_dict(today_clicks, 2, id)
    elif key == 2:
        title = "Private"
        total_url = url_list1.count()
        total_clicks = Private_URL.objects.filter(user=request.user).aggregate(
            Sum("clicks")
        )["clicks__sum"]
        total_clicks_list = Private_URL_Log.objects.filter(user=request.user)
        today_clicks = Private_URL_Log.objects.filter(user=request.user, url_log=date)
        Total_public_url = return_dict(url_list1, 0, id)
        Total_number_click = return_dict(total_clicks_list, 1, id)
        today_url_clicks = return_dict(today_clicks, 2, id)
    else:
        title = "Custom"
        total_url = url_list2.count()
        total_clicks = Custom_URL.objects.filter(user=request.user).aggregate(
            Sum("clicks")
        )["clicks__sum"]
        total_clicks_list = Custom_URL_Log.objects.filter(user=request.user)
        today_clicks = Custom_URL_Log.objects.filter(user=request.user, url_log=date)
        Total_public_url = return_dict(url_list2, 0, id)
        Total_number_click = return_dict(total_clicks_list, 1, id)
        today_url_clicks = return_dict(today_clicks, 2, id)

    tv, td = [row for row in Total_public_url], [
        Total_public_url[row] for row in Total_public_url
    ]
    tv1, td1 = [row for row in Total_number_click], [
        Total_number_click[row] for row in Total_number_click
    ]
    tv2, td2 = [row for row in today_url_clicks], [
        today_url_clicks[row] for row in today_url_clicks
    ]
    #
    today_clicks = today_clicks.aggregate(Sum("clicks"))
    today_clicks = today_clicks["clicks__sum"]
    if today_clicks == None:
        today_clicks = 0
    # if id == 1:
    context = {
        "title": title,
        "url_id": key,
        "total_url": total_url,
        "total_clicks": total_clicks,
        "url_list": url_list,
        "url_list1": url_list1,
        "url_list2": url_list2,
        "today_clicks": today_clicks,
        "label_value": td,
        "label_date": tv,
        "label_value1": td1,
        "label_date1": tv1,
        "label_value2": td2,
        "label_date2": tv2,
    }
    return context


def public_reports(request, id):
    if request.user.is_authenticated and not request.user.is_staff:
        context = reports(request, 1, id)
        return render(request, "includes/main.html", context)
    else:
        return redirect("/login")


def private_reports(request, id):
    if request.user.is_authenticated and not request.user.is_staff:
        context = reports(request, 2, id)
        # print(id)
        return render(request, "includes/main.html", context)
    else:
        return redirect("/login")


def custom_reports(request, id):
    if request.user.is_authenticated and not request.user.is_staff:
        context = reports(request, 3, id)
        # print(id)
        return render(request, "includes/main.html", context)
    else:
        return redirect("/login")
