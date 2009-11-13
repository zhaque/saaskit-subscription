### -*- coding: utf-8 -*- ####################################################

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings

from subscription.models import UserSubscription

class SubscriptionMiddleware(object):

    def process_exception(self, request, exception):
        if type(exception) == UserSubscription.DoesNotExist:
            return redirect('subscription_list')
        