### -*- coding: utf-8 -*- ####################################################

from datetime import datetime, date, timedelta
import calendar

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TransactionTestCase, TestCase
#from django.core.exceptions import ValidationError
#from django.core.urlresolvers import reverse

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from subscription.models import Subscription, UserSubscription, Transaction

class ModelTest(TestCase):
    fixtures = ['test_subscription.json']
    
    def setUp(self):
        #self.user = User.objects.get(username='test_user')
        #self.client.login(username=self.user.username, password='test')
        
        self.silver_sub = Subscription.objects.get(id=1)
        self.gold_sub = Subscription.objects.get(id=2)
        
        self.test_user = User.objects.get(id=1)
        self.silver_user = User.objects.get(username='silver_user')
        self.gold_user = User.objects.get(username='gold_user')
    
    def tearDown(self):
        pass
    
    def test_user_subscription(self):
        """ get 'subscription' attribute from all users"""
        #this user has no subscription
        self.assertRaises(UserSubscription.DoesNotExist, lambda : self.test_user.subscription)
    
        #silver subscription
        self.assertEqual(self.silver_user.subscription.subscription, self.silver_sub)
        
        #gold one
        self.assertEqual(self.gold_user.subscription.subscription, self.gold_sub)
    
    def test_get_initial_subscription(self):
        """ do test_user's subscription """
        us = self.silver_sub.subscribe(self.test_user)
        
        self.assertEqual(us.user, self.test_user)
        self.assertEqual(us.subscription, self.silver_sub)
        
        self.assertEqual(self.test_user.subscription.subscription, self.silver_sub)
    
    def test_change_subscription(self):
        """ do change silver_user's subscription """
        us = self.gold_sub.subscribe(self.silver_user)
        
        self.assertEqual(us.user, self.silver_user)
        self.assertEqual(us.subscription, self.gold_sub)
        
        self.assertEqual(self.silver_user.subscription.subscription, self.gold_sub)
    
    def test_expiration_initial(self):
        """ check expiration dates, passed by initialization """
        #silver plan has 21 day trial period
        self.assertEqual(self.silver_user.subscription.expires, date.today() + timedelta(21))
        
        #gold plan has 30 days recurrence repiod
        self.assertEqual(self.gold_user.subscription.expires, date.today() + timedelta(30))
    
    def test_permissions(self):
        """ test permission related functionality """
        #Firstly, check backend. 
        #We use special backend, he extend default ModelBackend by subscription's permissions
        self.assertTrue('subscription.backends.UserSubscriptionBackend' in settings.AUTHENTICATION_BACKENDS)
        
        #We didn't set any special permissions in our subscriptions
        #test_user did'nt subscribed, so, he shouldn't have any permissions
        self.assertEquals(self.test_user.get_all_permissions(), set([]))
        #silver and gold plans have not passed any specific permissions 
        self.assertEquals(self.silver_user.get_all_permissions(), set([]))
        self.assertEquals(self.gold_user.get_all_permissions(), set([]))
        
        #Add some permission to gold plan
        perm = Permission.objects.create(name="test", 
                                         content_type=ContentType.objects.get(name="subscription"), 
                                         codename="test")
        self.gold_sub.permissions.add(perm)
        self.gold_sub.save()
        
        #test_user did'nt subscribed, so, he shouldn't have any permissions
        self.assertEquals(self.test_user.get_all_permissions(), set([]))
        #silver plan was not changed
        self.assertEquals(self.silver_user.get_all_permissions(), set([]))
        self.assertEquals(self.gold_user.get_all_permissions(), set([u'subscription.test']))
        
        #deactivate subscription
        self.gold_user.subscription.active = False
        self.gold_user.subscription.save()
        
        #gold user must have his permissions anyway before his billing cycle ends. 
        
        self.gold_user = User.objects.get(username='gold_user')
        self.assertEquals(self.gold_user.get_all_permissions(), set([u'subscription.test']))
        