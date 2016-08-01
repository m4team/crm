from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'replies'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<customer_id>[0-9]+)/$', views.customer_chat, name = 'customer_chat'),
    url(r'^thread/(?P<thread_id>[0-9]+)/$', views.thread, name = 'thread'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
