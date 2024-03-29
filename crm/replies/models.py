from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import utils as u

class Customer(models.Model):
    emd5 = models.CharField(max_length=32)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_latest_thread(self):
        threads = self.thread_set.filter(closed=False).all()
        try:
            return sorted(threads, key=lambda thread: thread.latest_activity(),
                          reverse=True)[0] # None value would be sorted last
        except IndexError:
            return None
        
        
class Agent(models.Model):
    user = models.OneToOneField(User, null=True)
    ext_user_id = models.IntegerField() # external id from Pentius
    full_name = models.CharField(max_length=100)
    user_level = models.IntegerField()

    def __str__(self):
        return self.full_name

class Thread(models.Model):
    customer = models.ForeignKey(Customer)
    topic = models.CharField(max_length=50, default='Conversation')
    public = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    agents = models.ManyToManyField(Agent)
    
    def __str__(self):
        return self.topic
    
    def latest_activity(self):
        """ 
        Return the last time this thread has a message
        Return None if thread doesn't have any message
        """
        try:
            return max([x.timestamp_ts for x in self.message_set.all()])
        except ValueError: # no messages yet
            return None

    def responded(self):
        """ Return False if the last message is from the customer"""
        try:
            return not self.message_set.order_by('-timestamp_ts')[0].inbound
        except:
            return True
    
    
class Brand(models.Model):
    brand = models.CharField(max_length=100, unique=True)
    external_id = models.IntegerField(default=0)

    def __str__(self):
        return self.brand

    
class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    from_agent = models.ForeignKey(Agent, null=True, blank=True)
    inbound = models.BooleanField(default=False)
    content = models.TextField()
    content_text = models.TextField(null=True, blank=True)
    timestamp_ts = models.DateTimeField(default=timezone.now)
    subject_line = models.CharField(max_length=100, null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True, blank=True)
    external_id = models.CharField(max_length=100, null=True,
                                   blank=True, unique=True) # email token
    
    class Meta:
        ordering = ['timestamp_ts']
        
    def __str__(self):
        return self.content[:50]

    def handle(self):
        if self.inbound:
            return self.thread.customer.first_name
        else:
            return self.from_agent.full_name
        
    def web_view(self):
        return u.extract_link_html(u.extract_img_html(self.content))
