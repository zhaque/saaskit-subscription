### -*- coding: utf-8 -*- ####################################################

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse

from subscription.models import Subscription, UserSubscription, Transaction

class ClientTest(TransactionTestCase):
    fixtures = ['test_subscription.json']
    
    def setUp(self):
        #self.user = User.objects.get(username='test_user')
        #self.client.login(username=self.user.username, password='test')
        
        self.free_sub = Subscription.objects.get(id=1)
        self.silver_sub = Subscription.objects.get(id=2)
        
    def tearDown(self):
        pass
    
    def test_middleware(self):
        """ 
            Create new user. He will have no subscribtion. 
            So, middleware should redirect every request to subscription page
        """
        #firstly, check existence in settings parameter MIDDLEWARE_CLASSES
        self.assertTrue('subscription.middleware.SubscriptionMiddleware' in settings.MIDDLEWARE_CLASSES)
        
        #non-authnticated user
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        #create and authenticate user
        test_user = User.objects.create_user('testuser', 'test@example.com', 'testpw')
        self.client.login(username=test_user.username, password='testpw')
        
        response = self.client.get('/')
        self.assertRedirects(response, reverse('subscription_list'), target_status_code=302)
        