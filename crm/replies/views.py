from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader

from .models import Customer, Thread, Message
from .forms import MessageForm

from datetime import datetime
import requests

# HARD_CODED LOMAN API
LOMAN_API_URL = "http://208.95.61.102:5049/"

def index(request):
    return HttpResponse("Welcome to CRM")

def customer_chat(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {
        'customer' : customer
    }
    return render(request, 'replies/customer_chat.html', context)

def thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # send email
            try:
                subject_line = form.cleaned_data['subject_line']
            except KeyError:
                # Get subject line of the previous inbound message
                subject_line = thread.message_set.filter(inbound=True).order_by('-timestamp_ts')[0].subject_line
            data = {
                'agentID': request.user.agent.ext_user_id,
                'body': form.cleaned_data['content'],
                'brand': 'eScore', # Ugh
                'fromName': request.user.agent.full_name,
                'emailTo': thread.customer.emd5, # Edit Loman API to accept emd5
                'subject': subject_line
            }
            print data
            #r = requests.post('%s/send/' % LOMAN_API_URL, json=data)
            # Save record to database
            msg = Message(content=form.cleaned_data['content'],
                          from_agent=request.user.agent,
                          inbound=False,
                          timestamp_ts=datetime.now(),
                          thread=thread)
            msg.save()
    else:
        form = MessageForm()
    # Load new thread object to include the new message
    thread = get_object_or_404(Thread, pk=thread_id)
    context = {
        'thread': thread,
        'form': form
    }
    return render(request, 'replies/thread.html', context)


    
