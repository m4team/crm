from django.contrib import admin

from .models import Agent, Customer, Thread, Message

admin.site.register([Agent, Customer, Thread, Message])
