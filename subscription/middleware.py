### -*- coding: utf-8 -*- ####################################################

from django.shortcuts import redirect

from subscription.models import UserSubscription

class SubscriptionMiddleware(object):
    
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                sub = request.user.subscription
            except UserSubscription.DoesNotExist:
                return redirect('subscription_list')
        