### -*- coding: utf-8 -*- ####################################################

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings

from subscription.models import UserSubscription

class SubscriptionMiddleware(object):
    
    def process_request(self, request):
        if request.user.is_authenticated() \
        and not request.path.startswith(reverse('subscription_list')) \
        and not request.path.startswith(settings.MEDIA_URL):
            try:
                sub = request.user.subscription
            except UserSubscription.DoesNotExist:
                return redirect('subscription_list')
