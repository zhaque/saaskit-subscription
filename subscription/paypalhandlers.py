### -*- coding: utf-8 -*- ####################################################
""" Handle PayPal signals """

from django.contrib.auth.models import User

import paypal.standard.ipn.signals

from subscription.signals import paid
from subscription.models import Subscription

def get_subscription(payment):
    try:
        return Subscription.objects.get(id=int(payment.item_number))
    except (ValueError, Subscription.DoesNotExist):
        pass

def get_user(payment):
    try:
        return User.objects.get(id=int(payment.custom))
    except (ValueError, User.DoesNotExist):
        pass


def handle_subscription_signup(sender, **kwargs):
    subscription = get_subscription(sender)
    if subscription is not None:
        subscription.subscribe(get_user(sender))
paypal.standard.ipn.signals.subscription_signup.connect(handle_subscription_signup)
paypal.standard.ipn.signals.subscription_modify.connect(handle_subscription_signup)


def handle_payment_was_successful(sender, **kwargs):
    user = get_user(sender)
    if user is not None:
        us = user.subscription
        paid.send(us, payment=sender)
        us.extend()
        us.activate()
paypal.standard.ipn.signals.payment_was_successful.connect(handle_payment_was_successful)
paypal.standard.ipn.signals.recurring_payment.connect(handle_payment_was_successful)


def handle_subscription_cancel(sender, **kwargs):
    user = get_user(sender)
    if user is not None:
        user.subscription.cancel()
paypal.standard.ipn.signals.subscription_cancel.connect(handle_subscription_cancel)


def handle_subscription_eot(sender, **kwargs):
    user = get_user(sender)
    if user is not None:
        user.subscription.delete()
paypal.standard.ipn.signals.subscription_eot.connect(handle_subscription_eot)
