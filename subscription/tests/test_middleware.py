### -*- coding: utf-8 -*- ####################################################

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponse

from subscription.models import Subscription, UserSubscription, Transaction
from subscription.middleware import SubscriptionMiddleware

class MiddlewareTest(TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_middleware(self):
        """ 
            emulate real response, when raises an exception UserSubscription.DoesNotExist
            It means, that some user has no subscription.
            So, middleware should redirect every that request to subscription page
        """
        #firstly, check existence in settings parameter MIDDLEWARE_CLASSES
        self.assertTrue('subscription.middleware.SubscriptionMiddleware' in settings.MIDDLEWARE_CLASSES)
        
        def raise_exception(request):
            raise UserSubscription.DoesNotExist("matching query does not exist.")
        
        sub_middleware = SubscriptionMiddleware()
        request = WSGIRequest({'REQUEST_METHOD':'GET'})
        try:
            response = raise_exception(request)
        except Exception, e:
            response = sub_middleware.process_exception(request, e)
        
        self.assertEqual(response['Location'], reverse('subscription_list'))
        
        def not_raise_anything(request):
            return HttpResponse('everything is OK')
        
        try:
            response = not_raise_anything(request)
        except Exception, e:
            response = sub_middleware.process_exception(request, e)
        
        self.assertEqual(type(response), HttpResponse)
        