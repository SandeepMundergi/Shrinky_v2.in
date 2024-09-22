from django.contrib import admin

from .models import *

# from .models import guest_url, UserProfile

# Register your models here.

admin.site.register(guest_url)
admin.site.register(User)
admin.site.register(Public_URL)
admin.site.register(Private_URL)
admin.site.register(Custom_URL)
admin.site.register(Public_URL_Log)
admin.site.register(Private_URL_Log)
admin.site.register(Custom_URL_Log)

# admin.site.register(UserProfile)
