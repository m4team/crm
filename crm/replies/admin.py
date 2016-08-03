from django.contrib import admin

from .models import Agent, Customer, Thread, Message, Brand

admin.site.register([Agent, Customer, Thread, Message, Brand])
