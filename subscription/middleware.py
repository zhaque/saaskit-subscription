### -*- coding: utf-8 -*- ####################################################

from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from subscription.models import UserSubscription

class SubscriptionMiddleware(object):
    
    def process_request(self, request):
        if request.user.is_authenticated() and request.path != reverse('subscription_list'):
            try:
                sub = request.user.subscription
            except UserSubscription.DoesNotExist:
                return redirect('subscription_list')
        