### -*- coding: utf-8 -*- ####################################################
""" Handle PayPal signals """

import logging

from django.contrib.auth.models import User

from paypal.standard import ipn

from subscription.models import Transaction, Subscription
import signals

logger = logging.getLogger('subscription')

def get_subscription(payment):
    try:
        return Subscription.objects.get(id=int(payment.item_number))
    except (ValueError, Subscription.DoesNotExist), err:
        logger.debug(err)
        raise

def get_user(payment):
    try:
        return User.objects.get(id=int(payment.custom))
    except (ValueError, User.DoesNotExist):
        logger.debug(err)
        raise


def handle_subscription_signup(sender, **kwargs):
    subscription = get_subscription(sender)
    us = subscription.subscribe(get_user(sender))
    
    signals.subscribed.send(us, payment=sender)
ipn.signals.subscription_signup.connect(handle_subscription_signup)
ipn.signals.subscription_modify.connect(handle_subscription_signup)

def handle_payment_was_successful(sender, **kwargs):
    user = get_user(sender)
    us = user.subscription
    if sender.mc_gross == us.subscription.subscription.price:
        us.extend()
        us.active = True
        us.save()
#===============================================================================
#            Transaction(user=user, subscription=subscription, ipn=sender,
#                        event=Transaction.EVENT_PAYMENT, amount=sender.mc_gross
#                        ).save()
#===============================================================================
        signals.paid.send(us, payment=sender)
    else:
        Transaction(user=user, subscription=us.subscription.subscription, ipn=sender,
                    event=Transaction.EVENT_PAYMENT_INCORRECT, amount=sender.mc_gross
                    ).save()
ipn.signals.payment_was_successful.connect(handle_payment_was_successful)

#===============================================================================
# def handle_payment_was_flagged(sender, **kwargs):
#    user = get_user(sender)
#    us = user.subscription
#    if us:
#        Transaction(user=user, subscription=user.subscription.subscription, ipn=sender,
#                    event=Transaction.EVENT_PAYMENT_FLAGGED, amount=sender.mc_gross
#                    ).save()
#        #signals.event.send(s, ipn=sender, subscription=s, user=u, event='flagged')
# ipn.signals.payment_was_flagged.connect(handle_payment_was_flagged)
#===============================================================================

def handle_subscription_cancel(sender, **kwargs):
    user = get_user(sender)
    us = user.subscription
    us.active = False
    us.save()
    Transaction(user=user, subscription=us.subscription, ipn=sender,
                event=Transaction.EVENT_CANCELLED, amount=sender.mc_gross
                ).save()
ipn.signals.subscription_cancel.connect(handle_subscription_cancel)

def handle_subscription_eot(sender, **kwargs):
    us = get_user(sender).subscription
    us.delete()
#===============================================================================
#    Transaction(user=user, subscription=us.subscription, ipn=sender,
#                event=Transaction.EVENT_REMOVED, amount=sender.mc_gross
#                ).save()
#===============================================================================
    signals.unsubscribed.send(us, payment=sender)
ipn.signals.subscription_eot.connect(handle_subscription_eot)
