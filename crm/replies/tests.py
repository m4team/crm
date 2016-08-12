from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from models import Agent, Customer, Thread, Message, Brand

class MessageAPITests(TestCase):

    def setUp(self):
        # create objects here
        self.test_user = User.objects.create(username='tester', password='1234')
        self.test_agent = Agent.objects.create(user=self.test_user, ext_user_id=1234,
                                               full_name='Tester',
                                               user_level='9')
        self.test_ctmr = Customer.objects.create(
            emd5='ca5287d3089183d349c45242ffa3ee7b',
            first_name='Test',
            last_name='Customer'
        )
        self.test_brand = Brand.objects.create(brand='TestBrand',
                                               external_id=1)
        
    def test_add_reply(self):
        data = {
            'emd5': self.test_ctmr.emd5,
            'message_html': '<p>Test reply</p>',
            'message_text': 'Test reply',
            'insert_ts': str(timezone.now()),
            'smtp_id': 'test_id',
            'subject': 'Test subject'
        }
        response = self.client.post(reverse('replies:add_reply'), data)
        self.assertEqual(response.status_code, 200)

    def test_add_message_no_thread(self):
        data = {
            'emd5': self.test_ctmr.emd5,
            'body': 'Hello this is a test',
            'timestamp_ts': str(timezone.now()),
            'token': 'test_token',
            'subject': 'Test subject',
            'brand': self.test_brand.external_id,
            'agent_id': self.test_agent.ext_user_id,
        }
        response = self.client.post(reverse('replies:add_message'), data)
        print response.content
        print response.reason_phrase
        self.assertEqual(response.status_code, 200)


    def test_add_message_thread(self):
        test_thr = Thread.objects.create(customer=self.test_ctmr)
        data = {
            'emd5': self.test_ctmr.emd5,
            'body': 'Hello this is a test',
            'timestamp_ts': str(timezone.now()),
            'token': 'test_token2',
            'subject': 'Test subject',
            'brand': self.test_brand.external_id,
            'agent_id': self.test_agent.ext_user_id,
            'thread_id': test_thr.id
        } 
        response = self.client.post(reverse('replies:add_message'), data)
        self.assertEqual(response.status_code, 200)


    def test_add_existing_message(self):
        thrd = Thread.objects.create(customer=self.test_ctmr)
        msg = Message.objects.create(
            thread=thrd,
            inbound=True,
            content='Blah blah',
            external_id='token1'
        )
        msg.save()
        data = {
            'emd5': self.test_ctmr.emd5,
            'message_html': '<p>Test reply</p>',
            'message_text': 'Test reply',
            'insert_ts': str(timezone.now()),
            'smtp_id': 'token1',
            'subject': 'Test subject'
        }
        response = self.client.post(reverse('replies:add_reply'), data)
        self.assertEqual(response.status_code, 200)
                                     
