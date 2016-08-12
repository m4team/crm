from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.utils import timezone
from django.contrib import messages
from django.db import IntegrityError

from .models import Customer, Thread, Message, Agent, Brand
from .forms import MessageForm

import requests

# HARD_CODED LOMAN API
LOMAN_API_URL = "http://208.95.61.102:5049"

def index(request):
    context = {
        'agent': request.user.agent
    }
    return render(request, 'replies/index.html', context)

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
            try:
                brand = form.cleaned_data['brand']
            except KeyError:
                brand = thread.message_set.filter(inbound=False).order_by('-timestamp_ts')[0].brand
            data = {
                'agentID': request.user.agent.ext_user_id,
                'body': form.cleaned_data['content'],
                'brand': brand.brand,
                'fromName': request.user.agent.full_name,
                'emd5': thread.customer.emd5,
                'subject': subject_line,
                'thread_id': thread.id
            }
            r = requests.post('%s/send' % LOMAN_API_URL, json=data)
            if r.ok:
                # Save record to database
                msg = Message(content=form.cleaned_data['content'],
                              from_agent=request.user.agent,
                              inbound=False,
                              timestamp_ts=timezone.now(),
                              thread=thread,
                              subject_line=subject_line,
                              brand=brand,
                              external_id = r.json().get('token'))
                msg.save()
            else:
                messages.add_message(
                    request, messages.ERROR,
                    'Failed to send your message. Please try again later.'
                )
    else:
        form = MessageForm()
    # Load new thread object to include the new message
    thread = get_object_or_404(Thread, pk=thread_id)
    context = {
        'thread': thread,
        'form': form
    }
    return render(request, 'replies/thread.html', context)


def customer_profile(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {
        'customer' : customer
    }
    return render(request, 'replies/customer_profile.html', context)

def process_reply(request):
    """Process replies and messages raw data"""
    # post request for replies
    # each request have:
    # emd5, message_html, message_text, insert_ts
    # smtp_id, subject
    if request.method != 'POST':
        return HttpResponse(405)
    else:
        data = request.POST
        emd5 = data['emd5']
        customer = get_object_or_404(Customer, emd5=emd5) # or create a record
        thread = customer.get_latest_thread()
        if thread == None:
            # create new thread
            thread = Thread(customer=customer)
            thread.save()
        try:
            msg, created = Message.objects.get_or_create(
                thread=thread, inbound=True, content=data['message_html'],
                content_text=data.get('message_text'),
                timestamp_ts=data.get('insert_ts'),
                external_id=data.get('smtp_id'),
                subject_line=data.get('subject')
            )
        except IntegrityError: # duplicate external_id
            pass
        return HttpResponse(200, 'Success: Message saved')

def process_message(request):    
    """Process replies and messages raw data"""
    # post request for message
    # each request have:
    # emd5, body, timestamp_ts
    # token, subject, brand, agent_id, thread_id
    if request.method != 'POST':
        return HttpResponse(405)
    else:
        data = request.POST
        try:
            thread_id = data['thread_id']
            thread = get_object_or_404(Thread, pk=thread_id)
        except KeyError:
            customer = get_object_or_404(Customer, emd5=data.get('emd5'))
            thread = customer.get_latest_thread()
            if thread == None:
                thread = Thread(customer=customer)
                thread.save()
        brand = get_object_or_404(Brand, brand=data.get('brand'))
        agent = get_object_or_404(Agent, ext_user_id=int(data.get('agent_id')))
        try:
            msg, created = Message.objects.get_or_create(
                thread=thread, inbound=False, content=data['body'],
                timestamp_ts=data.get('timestamp_ts'),
                external_id=data.get('token'),
                subject_line=data.get('subject'),
                brand=brand,
                from_agent=agent
            )
        except IntegrityError: # Duplicate external id
            pass
        return HttpResponse(200, 'Success: Message Saved')
            
